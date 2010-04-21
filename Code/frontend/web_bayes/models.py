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
        
#    def CPT(self,child_state,*args):
#        query = CPTValue.objects.filter(child_state = child_state)
#        for state in args:           
#             query.filter(state_in = parent_states)
#        if query.count() == 0:
#            value = CPTValue(child_state = childstate)
#            for state in args:                       
#                value.parent_states.add(state)
#        else
#            return query[0]
    
    def parent_nodes(self): 
        for edge in self.parent_edges.all():
            yield edge.parent_node
     
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
    
    def delete(self, *args, **kwargs):            
        self.dependant_values.all().delete();
        super(State, self).delete(*args, **kwargs)        
    
    def __unicode__(self):
        return self.name
    
class CPTValue(models.Model):    
    child_state = models.ForeignKey(State,related_name="defining_values")
    parent_states = models.ManyToManyField(State,related_name="dependant_values")
    value = models.FloatField()

admin.site.register(CPTValue)   
