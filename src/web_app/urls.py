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
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    #Admin
    (r'^admin/', include(admin.site.urls)),
    (r'^admin_docs/', include('django.contrib.admindocs.urls')),
    
    #Login and Logout
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {
        'template_name' : 'web_bayes/login.html',
    },"login"),
    
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {
        'next_page' : '/',
    },"logout"),
    
    #Carbon App
    (r'', include('web_bayes.urls')),    
    )
                       
urlpatterns += patterns('django.views.static',
(r'^media/(?P<path>.*)$', 
    'serve', {
    'document_root': settings.MEDIA_ROOT,
    'show_indexes': True }),)

