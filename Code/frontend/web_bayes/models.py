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
        
admin.site.register(Node)
            
class Edge(models.Model):
    network = models.ForeignKey(Network,related_name="edges",editable=False)
    parent_node = models.ForeignKey(Node,related_name="child_edges")
    child_node = models.ForeignKey(Node,related_name="parent_edges")
    
    def __unicode__(self):
        return '%s->%s'%(self.parent_node,self.child_node)    

admin.site.register(Edge)
