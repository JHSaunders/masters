import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import Sum

class Network(models.Model):
    name = models.CharField(max_length=100)
    
    def get_absolute_url(self):
        return "/network/%i"%(self.id,)
    
    def free_nodes(self):
        return self.nodes.filter(cluster=None)
        
    def __unicode__(self):
        return self.name

admin.site.register(Network)

class Cluster(models.Model):
    name = models.CharField(max_length=100)
    network = models.ForeignKey(Network,related_name="clusters",editable=False)

    def __unicode__(self):
        return self.name

admin.site.register(Cluster)
            
class Node(models.Model):
    name = models.CharField(max_length=100)
    network = models.ForeignKey(Network,related_name="nodes",editable=False)
    cluster = models.ForeignKey(Cluster,related_name="nodes",null=True,blank=True)
    
    def __unicode__(self):
        return self.name
        
    def slug(self):
        return self.name.replace(" ","_")
    
    def parent_nodes(self): 
        parents=[]
        for edge in self.parent_edges.all():
            parents.append(edge.parent_node)        
        return parents
    
    def is_root(self):
        return len(self.parent_nodes())==0
        
    def cpt_value(self,child_state,parent_states):
        query = CPTValue.objects.filter(child_state = child_state)
        
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
    
    def get_value_sets(self):
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
           return []
        
        results = []
        
        while state_count<max_state_count:                
            parent_states = []
            for i in range(len(parent_nodes)):
                parent_states.append(parent_nodes[i].states.all()[current_states[i]])
            
            values = []
            for state in self.states.all():
                values.append(self.cpt_value(state,parent_states))
            
            results.append((parent_states,values))
                        
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
        
        return results
    
    def normalise_cpt_values(self):
        for tup in self.get_value_sets():
            total = 0
            for value in tup[1]:
                total+=value.value
            for value in tup[1]:
                if total>0:
                    value.value = value.value/total
                else:
                    value.value = 1.0/len(tup[1])
                    
                value.save()
                
    def normalise_probabilities(self):
        total = 0
        for states in self.states.all():
            total+=states.probability
        
        for state in self.states.all():
            if total>0:
                state.probability/=total
            else:
                state.probaility= 1/self.states.count()
            state.save()
        
    def clean_cpt_values(self):
        pass
    
    def normalise_node(self):
        self.normalise_probabilities()        
        self.clean_cpt_values()        
        self.normalise_cpt_values()
        
admin.site.register(Node)
            
class Edge(models.Model):
    network = models.ForeignKey(Network,related_name="edges",editable=False)
    parent_node = models.ForeignKey(Node,related_name="child_edges")
    child_node = models.ForeignKey(Node,related_name="parent_edges")
    
    def __unicode__(self):
        return '%s->%s'%(self.parent_node,self.child_node)    

admin.site.register(Edge)

class State(models.Model):
    node = models.ForeignKey(Node,related_name="states",editable=False)
    name = models.CharField(max_length=100)
    probability = models.FloatField(blank=True)
    
    def delete(self, *args, **kwargs):            
        self.dependant_values.all().delete();
        super(State, self).delete(*args, **kwargs)        
    
    def save(self,*args,**kwargs):
        if self.probability==None:
            self.probability = 0.0
        super(State, self).save(*args, **kwargs)        
        
    def __unicode__(self):
        return self.name
    
class CPTValue(models.Model):    
    child_state = models.ForeignKey(State,related_name="defining_values")
    parent_states = models.ManyToManyField(State,related_name="dependant_values")
    value = models.FloatField(default=0.0)

admin.site.register(CPTValue)   
