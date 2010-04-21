from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.list_networks,name="list_networks"),
    url(r'^network/(?P<network_id>\d+)$', views.view_network,name="view_network"),
    
    url(r'^network/(?P<network_id>\d+)/definition.svg$', views.network_definition_visualisation_svg,name="network_definition_svg"),
    url(r'^network/(?P<network_id>\d+)/definition.png$', views.network_definition_visualisation_png,name="network_definition_png"),
        
    url(r'^network/(?P<network_id>\d+)/dot.txt$', views.network_definition_visualisation_dot,name="network_definition_dot"),
        
    url(r'^create_network$', views.create_network,name="create_network"),
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
    
    )