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
    name = models.CharField(max_length=100)
    network = models.ForeignKey(Network,related_name="nodes",editable=False)
    description = models.CharField(max_length=256,blank=True)
    cluster = models.ForeignKey(Cluster,related_name="nodes", null=True, blank=True)
    node_class = models.CharField(max_length=15,default='C',choices=(('A','Action'),('U','Utility'),('C','Chance')))
    
    def __init__(self,*args,**kwargs):
        self.cpt_cached = False
        super(Node, self).__init__(*args, **kwargs)
    
    def __unicode__(self):
        return self.name
        
    def slug(self):
        return str(self.id)
    
    def parent_nodes(self): 
        parents=[]
        for edge in self.parent_edges.select_related().all():
            parents.append(edge.parent_node)        
        return parents
    
    def is_root(self):
        return len(self.parent_nodes())==0
    
    def is_observed(self):
        for state in self.states.all():
            if state.observed:
                return True
        return False    
    
    def cpt_value(self,child_state,parent_states):
        
        query = CPTValue.objects.select_related().filter(child_state = child_state)        
        for state in parent_states:            
            query = query.filter(parent_states = state)
            
        if query.count() == 0:
            value = CPTValue(child_state = child_state,value=0)            
            value.save()
            for state in parent_states:                       
                value.parent_states.add(state)
            value.save()
            return value
        else:
            return query[0]
    
    def get_indexed_value_sets(self):
        max_states = []
        state_count = 0
        max_state_count = 1
        current_states = []        
        parent_nodes = []
        for parent in self.parent_nodes():
            parent_nodes.append(parent)            
            max_states.append(parent.states.count())
            max_state_count*=parent.states.count()
            current_states.append(0)            

        if len(max_states)==0 or max_state_count == 0:
           return ([],[])
        
        results = []
        indexes = []
        
        while state_count<max_state_count:                
            parent_states = []
            state_indexes = []
            for i in range(len(parent_nodes)):
                parent_states.append(parent_nodes[i].states.all()[current_states[i]])
                state_indexes.append(current_states[i])
            
            values = []
            for state in self.states.all():
                values.append(self.cpt_value(state,parent_states))
            
            results.append((parent_states,values))
            
            indexes.append((state_indexes,values))
            
            state_count +=1
            running = True
            index = len(current_states) - 1
            
            while running:                
                current_states[index]+=1
                running = False
                if current_states[index]==max_states[index]:
                   current_states[index] = 0
                   running = True
                index-=1
        
        return (results,indexes)
    
    def get_value_sets(self):
        return self.get_indexed_value_sets()[0]
                
    def normalise_cpt_values(self):
        for tup in self.get_value_sets():
            total = 0
            for value in tup[1]:
                total+=value.value
            for value in tup[1]:
                old_value = value.value
                if total>0:
                    value.value = value.value/total
                else:
                    value.value = 1.0/len(tup[1])
                if value.value != old_value: 
                    value.save()
                
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
        #self.normalise_probabilities()        
        #self.clean_cpt_values()        
        #self.normalise_cpt_values()
        pass
        
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
    name = models.CharField(max_length=100)
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
    
class CPTValue(NetworkBase):
    child_state = models.ForeignKey(State,related_name="defining_values")
    parent_states = models.ManyToManyField(State,related_name="dependant_values")
    value = models.FloatField(default=0.0)
    
    @property
    def network(self):
        return self.child_state.network
    
admin.site.register(CPTValue)   
