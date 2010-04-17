import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import Sum

class Network(models.Model):
    name = models.CharField(max_length=100)
    
    def get_absolute_url(self):
        return "/network/%i"%(self.id,)
        
    def __unicode__(self):
        return self.name

admin.site.register(Network)

class Cluster(models.Model):
    name = models.CharField(max_length=100)
    network = models.ForeignKey(Network,related_name="clusters")
    
class Node(models.Model):
    name = models.CharField(max_length=100)
    network = models.ForeignKey(Network,related_name="nodes")
    cluster = models.ForeignKey(Cluster,related_name="nodes",null=True)
    
class Edge(models.Model):
    network = models.ForeignKey(Network,related_name="edges")
    parent_node = models.ForeignKey(Node,related_name="child_edges")
    child_node = models.ForeignKey(Node,related_name="parent_edges")
    

