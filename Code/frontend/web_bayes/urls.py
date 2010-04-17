
from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.list_networks,name="list_networks"),
    url(r'^network/(?P<network_id>\d+)$', views.view_network,name="view_network"),
    url(r'^create_network$', views.create_network,name="create_network"),
    url(r'^network/(?P<network_id>\d+)/properties$', views.edit_network_properties,name="network_properties"),
      
        )
