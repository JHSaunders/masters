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

