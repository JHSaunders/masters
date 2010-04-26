import pydoc
import datetime

from django.http import *
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.generic.simple import direct_to_template
from django.views.generic.create_update import create_object, update_object, delete_object
from django.views.generic.list_detail import object_detail, object_list
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

from models import *
from forms import *
from visualisation import DotBasicNetwork,VisualiseBasicNetwork,VisualiseInferenceNetwork
from inference import PerformInference

def help(req,thing):
    doc = pydoc.HTMLDoc()
    return HttpResponse(doc.document(thing))
    
def test(req):
    return HttpResponse("Hello world")

def list_networks(req):
    return object_list(req,Network.objects.all())

def view_network_definition(req,network_id):
    network = Network.objects.get(id = network_id)
    return direct_to_template(req,"web_bayes/network_definition.html",{"network":network,"map":VisualiseBasicNetwork(network,"cmapx")})

def network_definition_visualisation_svg(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='image/svg+xml')
    response['Content-Disposition'] = 'filename=network.svg'
    response.write(VisualiseBasicNetwork(network,"svg"))
    return response

def network_definition_visualisation_png(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='image/png')
    response['Content-Disposition'] = 'filename=network.png'
    response.write(VisualiseBasicNetwork(network,"png"))
    return response

def network_definition_visualisation_dot(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='text/plain')
    response.write(DotBasicNetwork(network))
    return response

def create_network(req):
    return create_object(req,model=Network)

def edit_network_properties(req,network_id):
    return update_object(req,model=Network,object_id=network_id)

def delete_network(req,network_id):
    return delete_object(req,model=Network,object_id=network_id,post_delete_redirect=reverse('list_networks'))
    
def create_node(req,network_id):
    node = Node(network = Network.objects.get(id = network_id))
    node.save()
    node.name = "New node %d" % node.id
    node.save()
    State(node = node,name="On",probability=0.5).save()
    State(node = node,name="Off",probability=0.5).save()
    
    return HttpResponseRedirect(reverse("view_node",args=[node.id]))
    
def view_node(req,node_id):
    node = Node.objects.get(id=node_id)
    StatesFormSet = inlineformset_factory(Node, State)    
        
    if req.method=="POST":
        details_form = NodeForm(req.POST,instance = node)
        states_formset = StatesFormSet(req.POST, req.FILES, instance=node)
        cpt_form = CPTForm(req.POST, node=node)
                         
        if cpt_form.is_valid() and details_form.is_valid() and states_formset.is_valid() :
            details_form.save()            
            for state in  states_formset.save(commit=False):
                state.node = node
                state.save()
            
            cpt_form.save_values()
            node.normalise_node()                
            if u'continue' in req.POST:                
                return HttpResponseRedirect(reverse("view_node",args=[node.id]))
            else:
                return HttpResponseRedirect(reverse("view_network",args=[node.network.id]))
                
        else:
            return HttpResponseRedirect(reverse("view_node",args=[node.id]))
    else:        
        details_form = NodeForm(instance = node)
        node.normalise_node()
        states_formset = StatesFormSet(instance=node)
        cpt_form = CPTForm(node=node)
        
    return direct_to_template(req,"web_bayes/node_form.html",
                                extra_context={"details_form":details_form,
                                               "states_formset":states_formset,
                                               "cpt_form": cpt_form,"node":node})

def delete_node(req,node_id):
    node = Node.objects.get(id=node_id)  
    return delete_object(req,model=Node,object_id=node_id,post_delete_redirect=reverse('view_network', args=[node.network.id]))

def create_edge(req,network_id):    
    if req.method=="POST":
        form = EdgeForm(req.POST,network=Network.objects.get(id=network_id))
        if form.is_valid():
            edge = form.save(commit=False)
            edge.network = Network.objects.get(id=network_id)
            edge.save()
            return HttpResponseRedirect(reverse('view_network', args=[edge.network.id]))
    else:
        form = EdgeForm(network=Network.objects.get(id=network_id))        
        
    return direct_to_template(req,"web_bayes/edge_form.html",extra_context={"form":form,"network":Network.objects.get(id=network_id)})
    
def view_edge(req,edge_id):
    edge = Edge.objects.get(id=edge_id)
    if req.method=="POST":
        form = EdgeForm(req.POST,instance=edge)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_network', args=[edge.network.id]))
    else:
        form = EdgeForm(instance=edge)        
        
    return direct_to_template(req,"web_bayes/edge_form.html",extra_context={"object":edge,"form":form,"network":edge.network})   

def delete_edge(req,edge_id):
    edge = Edge.objects.get(id=edge_id)  
    return delete_object(req,model=Edge,object_id=edge_id,post_delete_redirect=reverse('view_network', args=[edge.network.id]))

def view_cluster(req,cluster_id):
    cluster = Cluster.objects.get(id=cluster_id)
    return update_object(req,model=Cluster,object_id=cluster_id,post_save_redirect=reverse('view_network',args=[cluster.network.id]))

def delete_cluster(req,cluster_id):
    cluster = Cluster.objects.get(id=cluster_id)  
    return delete_object(req,model=Cluster,object_id=cluster_id,post_delete_redirect=reverse('view_network', args=[cluster.network.id]))

def create_cluster(req,network_id):
    cluster = Cluster(network = Network.objects.get(id = network_id))
    cluster.save()
    cluster.name = "New cluster %d" % cluster.id
    cluster.save()
    return HttpResponseRedirect(reverse("view_cluster",args=[cluster.id]))
    
def network_inference(req,network_id):
    network = Network.objects.get(id = network_id)
    return direct_to_template(req,"web_bayes/network_inference.html",{"network":network,"map":VisualiseInferenceNetwork(network,"cmapx")})
    
def network_inference_visualisation_svg(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='image/svg+xml')
    response['Content-Disposition'] = 'filename=network.svg'
    response.write(VisualiseInferenceNetwork(network,"svg"))
    return response

def perform_inference(req,network_id):
    network = Network.objects.get(id=network_id)
    if req.method=="POST":
        if u'perform' in req.POST:
            PerformInference(network)
            return HttpResponseRedirect(reverse("network_inference",args=[network_id]))          
    
    return direct_to_template(req,"web_bayes/perform_inference.html",{"network":network})
