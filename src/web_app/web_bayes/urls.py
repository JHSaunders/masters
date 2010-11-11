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
from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.list_networks,name="list_networks"),
    url(r'^$', views.list_networks,name="home"),
    
    url(r'^network/(?P<network_id>\d+)/defintion$', views.view_network_definition,name="network_definition"),
    
    url(r'^network/(?P<network_id>\d+)/defintion$', views.view_network_definition,name="view_network"),
    
    url(r'^network/(?P<network_id>\d+)/definition.svg$', views.network_definition_visualisation_svg,name="network_definition_svg"),
    url(r'^network/(?P<network_id>\d+)/definition.png$', views.network_definition_visualisation_png,name="network_definition_png"),
    url(r'^network/(?P<network_id>\d+)/dot.txt$', views.network_definition_visualisation_dot,name="network_definition_dot"),
    url(r'^network/(?P<network_id>\d+)/inference.svg$', views.network_inference_visualisation_svg,name="network_inference_svg"),
    
    url(r'^network/(?P<network_id>\d+)/xmlbif.xml$', views.network_xmlbif,name="network_xmlbif"),
    url(r'^network/(?P<network_id>\d+)/xbn.xml$', views.network_xbn,name="network_xbn"),    
    url(r'^network/(?P<network_id>\d+)/import_cluster$', views.import_cluster,name="import_cluster"),    
        
    url(r'^success$',views.success_response,name="success"),
        
    url(r'^create_network$', views.create_network,name="create_network"),
    url(r'^upload_network$', views.upload_network,name="upload_network"),
    url(r'^network/(?P<network_id>\d+)/properties$', views.edit_network_properties,name="network_properties"),
    url(r'^network/(?P<network_id>\d+)/delete$', views.delete_network,name="delete_network"),
    
    url(r'^create_node/(?P<network_id>\d+)$',views.create_node,name="create_node"),    
    url(r'^node/(?P<node_id>\d+)/view$', views.view_node,name="view_node"),   
    url(r'^node/(?P<node_id>\d+)/delete$', views.delete_node,name="delete_node"),

    url(r'^create_edge/(?P<network_id>\d+)$',views.create_edge,name="create_edge"),
    url(r'^edge/(?P<edge_id>\d+)/view$', views.view_edge, name="view_edge"),
    url(r'^edge/(?P<edge_id>\d+)/delete$', views.delete_edge,name="delete_edge"),
    
    url(r'^create_cluster/(?P<network_id>\d+)$',views.create_cluster,name="create_cluster"),        
    url(r'^cluster/(?P<cluster_id>\d+)/view$', views.view_cluster,name="view_cluster"),
    url(r'^cluster/(?P<cluster_id>\d+)/delete$', views.delete_cluster,name="delete_cluster"),
    url(r'^cluster/(?P<cluster_id>\d+)/copy$', views.copy_cluster,name="copy_cluster"),
        
    url(r'^network/(?P<network_id>\d+)/inference$', views.network_inference, name="network_inference"),
    
    url(r'^toggle_observation/(?P<state_id>\d+)$', views.toggle_observation, name="toggle_observation"), 
    
    url(r'^network/(?P<network_id>\d+)/perform_inference$', views.perform_inference, name="perform_inference"),        
    url(r'^network/(?P<network_id>\d+)/clear_inference$', views.clear_inference, name="clear_inference"),            
    )
