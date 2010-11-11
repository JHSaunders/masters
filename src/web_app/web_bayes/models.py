#Copyright 2010 James Saunders
#
#This file is part of Web BPDA.
#
#Web BPDA is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Web BPDA.  If not, see <http://www.gnu.org/licenses/>.

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import Sum
from django.db.models import F
from django.core.urlresolvers import reverse
from django.db import transaction

class NetworkBase(models.Model):
    class Meta:
        abstract = True
        
    def save(self,*args,**kwargs):        
        try:            
            self.network.update_version(self)
        finally:            
            super(NetworkBase, self).save(*args, **kwargs)
    
    def delete(self,*args,**kwargs):        
        try:
            self.network.update_version(self)
        finally:
            super(NetworkBase, self).delete(*args, **kwargs)
            
    def type_name(self):
        return self.__class__.__name__.lower()

class Network(NetworkBase):
    
    def __init__(self,*args,**kwargs):
        self.in_version_update=False
        super(Network, self).__init__(*args, **kwargs)
                        
    name = models.CharField(max_length=100)
    version = models.IntegerField(default=0,editable=False)
    backend = models.CharField(max_length=15,default='agrum-lazy',choices=(('openbayes-jt','Open Bayes using Join Tree'),('openbayes-mcmc','Open Bayes using MCMC'),('agrum-lazy','aGrUM using Lazy Propagation'),('agrum-gibbs','aGrUM usign Gibbs Sampling'))) 
    users = models.ManyToManyField(User,related_name="networks",blank=True)
    
    @property
    def network(self):
        return self
    
    def get_absolute_url(self):
        return reverse('view_network',args=[self.id])
    
    @property
    def free_nodes(self):
        return self.nodes.filter(cluster=None)
    
    def update_version(self,calling):
        if not self.in_version_update and not transaction.is_dirty():
            self.in_version_update = True            
            self.version+=1       
            self.save()
            self.in_version_update = False
            
    def __unicode__(self):
        return self.name

admin.site.register(Network)

class Cluster(NetworkBase):
    name = models.CharField(max_length=100)
    network = models.ForeignKey(Network,related_name="clusters",editable=False)

    def __unicode__(self):
        return self.name

admin.site.register(Cluster)
            
class Node(NetworkBase):
    
    class Meta:
        ordering =('id',)
            
    name = models.CharField(max_length=300)
    network = models.ForeignKey(Network,related_name="nodes",editable=False)
    description = models.TextField(max_length=1000,blank=True)
    cluster = models.ForeignKey(Cluster,related_name="nodes", null=True, blank=True)
    node_class = models.CharField(max_length=15,default='C',choices=(('A','Action'),('U','Utility'),('C','Chance')))
    cpts_string = models.CharField(max_length=10000,blank=True,editable=False)
    
    def __init__(self,*args,**kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self._cpt = None
   
    def __unicode__(self):
        return self.name
        
    def slug(self):
        return str(self.id)
    
    def parent_nodes(self): 
        parents=[]
        for edge in self.parent_edges.select_related().select_related():
            parents.append(edge.parent_node)        
        return parents
    
    def is_root(self):
        return len(self.parent_nodes())==0
    
    def is_observed(self):
        for state in self.states.all():
            if state.observed:
                return True
        return False    
    
    def CPT(self):
        if self._cpt == None:
            self._cpt = CPT(self)
        return self._cpt
    
    def write_back_cpt_values(self):
        if self._cpt!=None:
            self.cpts_string = ",".join([str(cp) for cp in self.CPT().get_clean_cp_values()])
    
    def save(self,*args,**kwargs):
        self.write_back_cpt_values()
        super(Node, self).save(*args, **kwargs)     
                
    def normalise_probabilities(self):
        total = 0
        for states in self.states.all():
            total+=states.probability
        
        for state in self.states.all():
            old_state=state.probability
            
            if total>0:
                state.probability/=total
            else:
                state.probability= 1/self.states.count()
            
            if state.probability != old_state:
                state.save()
        
    def clean_cpt_values(self):
        pass
    
    def normalise_node(self):
        self.normalise_probabilities()

class CPT:
    def __init__(self,node):
        self.node = node
        self._indexes = self._get_indexes(self.node)
        
        if node.cpts_string.strip() != '':
            cps = [ float(cp) for cp in node.cpts_string.strip().split(",") ]
        else:
            cps = []
        self.set_cpt_values(cps)
            
    def _get_indexes(self,node):
        parent_nodes = node.parent_nodes()
        state_counts = [p.states.count() for p in parent_nodes]
        state_counts.append(node.states.count())
        
        cpt_count = 1
        for cnt in state_counts:
            cpt_count*=cnt
        cpt_count*= len(parent_nodes)>0 and node.states.count()>0 
        
        indexes=[]
                
        base_index = [0 for p in state_counts]
        divisors = [1 for p in state_counts]
        
        for i in range(len(state_counts)-2,-1,-1):
            divisors[i]=divisors[i+1]*state_counts[i+1]
       
        for cpt_index in range(cpt_count):
            index = []
            for (div,cnt) in zip(divisors,state_counts):
                index.append((cpt_index // div) % cnt)
            indexes.append(tuple(index))
        
        return indexes
    
    def set_cpt_values(self,values):
        self._cps = values[:len(self._indexes)]
        while len(self._cps)<len(self._indexes):
            self._cps.append(0.0)        
        #print self._cps        
        
    def get_cpt_values(self):
        return zip(self._indexes,self._cps)
    
    def get_cpt_rows(self):
        cnt_st = self.node.states.count()
        cps = self._cps
        rows = []
        
        for ri in range(len(cps)/cnt_st):
            index = self._indexes[ri*cnt_st][:-1]
            values =self._cps[ri*cnt_st:(ri+1)*cnt_st]
            rows.append((index,values))

        return rows
            
    def normalize_cpt_values(self):
        cnt_st = self.node.states.count()
        cps = self._cps
        cpt_normalised = []
        
        for ri in range(len(cps)/cnt_st):
            
            row =self._cps[ri*cnt_st:(ri+1)*cnt_st]
            sum = 0.0
            for v in row:
                sum+=v
            if sum ==0.0:
                for v in row:
                    cpt_normalised.append(1.0/cnt_st)
            else:    
                for v in row:
                    cpt_normalised.append(v/sum)

        self._cps = cpt_normalised                    
                        
    def get_clean_cp_values(self):
        self.normalize_cpt_values()
        return self._cps
        
admin.site.register(Node)

class NodeReasoningJustification(models.Model):
    node = models.ForeignKey(Node,related_name="reasons",editable=False)
    action = models.CharField(max_length=256)
    reason = models.CharField(max_length=256)
    version = models.IntegerField(editable=False)

admin.site.register(NodeReasoningJustification)
            
class Edge(NetworkBase):
    network = models.ForeignKey(Network,related_name="edges",editable=False)
    parent_node = models.ForeignKey(Node,related_name="child_edges")
    child_node = models.ForeignKey(Node,related_name="parent_edges")
    edge_class = models.CharField(max_length=15,default='R',choices=(('R','Resulting'),('I','Initiating'),('E','Enabling'),('IE','Initiating and Enabling')))    
    edge_effect = models.CharField(max_length=15,blank=True,null=True,default=None,choices=(('+','Positive'),('-','Negative')))    
    
    def __unicode__(self):
        return '%s->%s'%(self.parent_node,self.child_node)  

admin.site.register(Edge)

class State(NetworkBase):
    class Meta:
        ordering =('node','id')
    node = models.ForeignKey(Node,related_name="states",editable=False)
    name = models.CharField(max_length=300)
    probability = models.FloatField(blank=True)
    inferred_probability = models.FloatField(blank=True,null=True)
    observed = models.BooleanField(blank=True,default=False)
    
    @property
    def network(self):
        return self.node.network
    
    def delete(self, *args, **kwargs):            
        self.dependant_values.all().delete();
        super(State, self).delete(*args, **kwargs)        
    
    def save(self,*args,**kwargs):
        if self.probability==None:
            self.probability = 0.0
        super(State, self).save(*args, **kwargs)        
    
    def toggle_observed(self):
        if self.observed:
            self.observed = False
        else:
            for state in self.node.states.all():
                if state.observed:                    
                    state.toggle_observed()
            self.observed=True        
        self.save()
        
    def __unicode__(self):
        return self.name
admin.site.register(State)
