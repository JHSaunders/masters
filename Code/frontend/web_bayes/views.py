import pydoc
import datetime

from django.http import *
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.generic.simple import direct_to_template
from django.views.generic.create_update import create_object, update_object, delete_object
from django.views.generic.list_detail import object_detail, object_list
from django.core.urlresolvers import reverse

from models import *

def help(req,thing):
    doc = pydoc.HTMLDoc()
    return HttpResponse(doc.document(thing))
    
def test(req):
    return HttpResponse("Hello world")

def list_networks(req):
    return object_list(req,Network.objects.all())

def view_network(req,network_id):
    return object_detail(req,queryset=Network.objects.all(),object_id=network_id)

def create_network(req):
    return create_object(req,model=Network)

def edit_network_properties(req,network_id):
    return update_object(req,model=Network,object_id=network_id)
