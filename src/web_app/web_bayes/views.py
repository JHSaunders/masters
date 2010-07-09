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
from visualisation import DotBasicNetwork,VisualiseBasicNetwork,VisualiseInferenceNetwork,inline_svg
from inference import PerformInference, ClearInference

from interchange import write_xml_bif,write_xbn,upload_xbn

def help(req,thing):
    doc = pydoc.HTMLDoc()
    return HttpResponse(doc.document(thing))
    
def test(req):
    return HttpResponse("Hello world")

def success_response(req):
    return ok()

def ok():
    return HttpResponse("success",mimetype="text/plain")
    
def list_networks(req):
    return object_list(req,Network.objects.all())

def view_network_definition(req,network_id):
    network = Network.objects.get(id = network_id)
    return direct_to_template(req,"web_bayes/network_definition.html",
        {"network":network,
        "graph":inline_svg(VisualiseBasicNetwork(network,"svg"))}
        ,mimetype="application/xhtml+xml")
    

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

def network_xmlbif(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='text/xml')
    response['Content-Disposition'] = 'filename=%s.xml'% network.name.replace(' ','_')
    response.write(write_xml_bif(network));
    return response

def network_xbn(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='text/xml')
    response['Content-Disposition'] = 'filename=%s.xbn'% network.name.replace(' ','_')
    response.write(write_xbn(network))
    return response
    
def create_network(req):
    return create_object(req,model=Network)

def upload_network(req):
    
    if req.method=="POST":
        form = UploadForm(req.POST,req.FILES)
        if form.is_valid():
            network = upload_xbn(req.FILES['file'])
            return HttpResponseRedirect(reverse("view_network",args=[network.id]))
    else:        
        form = UploadForm()
    return direct_to_template(req,"web_bayes/upload_network.html",{"form":form})

def edit_network_properties(req,network_id):
    return update_object(req,model=Network,object_id=network_id)

def delete_network(req,network_id):
    return delete_object(req,model=Network,object_id=network_id,post_delete_redirect=reverse('list_networks'))
    
def create_node(req,network_id):
    node = Node(network = Network.objects.get(id = network_id))
    node.save()
    node.name = "New node %d" % node.id
    node.save()
    node.normalise_node()
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
        reasoning_form = ReasoningJustificationForm(req.POST)
                         
        if cpt_form.is_valid() and details_form.is_valid() and states_formset.is_valid() and reasoning_form.is_valid():
            details_form.save()            
            for state in  states_formset.save(commit=False):
                state.node = node
                state.save()
            
            cpt_form.save_values()
            node.normalise_node()                
            if reasoning_form.cleaned_data["reason"]!="" or reasoning_form.cleaned_data["action"]!="":
                NodeReasoningJustification(node=node,reason=reasoning_form.cleaned_data["reason"],action=reasoning_form.cleaned_data["action"],version=node.network.version).save()
            
            if u'continue' in req.POST:                
                return HttpResponseRedirect(reverse("view_node",args=[node.id]))
            else:
                return success_response(req)
                
        else:
            return HttpResponseRedirect(reverse("view_node",args=[node.id]))
    else:        
        details_form = NodeForm(instance = node)
        node.normalise_node()
        states_formset = StatesFormSet(instance=node)
        cpt_form = CPTForm(node=node)
        reasoning_form = ReasoningJustificationForm()
        
    return direct_to_template(req,"web_bayes/node_form.html",
                                extra_context={"details_form":details_form,
                                               "states_formset":states_formset,
                                               "cpt_form": cpt_form,
                                               "node":node,
                                               "reasoning_form":reasoning_form})

def delete_node(req,node_id):
    node = Node.objects.get(id=node_id)  
    return delete_object(req,model=Node,object_id=node_id,post_delete_redirect=reverse('success'),extra_context={'action_url':reverse('delete_node', args=[node_id])})

def create_edge(req,network_id):    
    if req.method=="POST":
        form = EdgeForm(req.POST,network=Network.objects.get(id=network_id))
        if form.is_valid():
            edge = form.save(commit=False)
            edge.network = Network.objects.get(id=network_id)
            edge.save()
            return success_response(req)
    else:
        form = EdgeForm(network=Network.objects.get(id=network_id))        
        
    return direct_to_template(req,"web_bayes/edge_form.html",extra_context={"form":form,"network":Network.objects.get(id=network_id)})
    
def view_edge(req,edge_id):
    edge = Edge.objects.get(id=edge_id)
    if req.method=="POST":
        form = EdgeForm(req.POST,instance=edge)
        if form.is_valid():
            form.save()
            return ok()
    else:
        form = EdgeForm(instance=edge)        
        
    return direct_to_template(req,"web_bayes/edge_form.html",extra_context={"object":edge,"form":form,"network":edge.network})   

def delete_edge(req,edge_id):
    edge = Edge.objects.get(id=edge_id)  
    return delete_object(req,model=Edge,object_id=edge_id,post_delete_redirect=reverse('success'), extra_context={'action_url':reverse('delete_edge', args=[edge_id])})

def view_cluster(req,cluster_id):
    cluster = Cluster.objects.get(id=cluster_id)
    return update_object(req,model=Cluster,object_id=cluster_id,post_save_redirect=reverse('success'))

def delete_cluster(req,cluster_id):
    cluster = Cluster.objects.get(id=cluster_id)  
    return delete_object(req,model=Cluster,object_id=cluster_id,post_delete_redirect=reverse('success'),extra_context={'action_url':reverse('delete_cluster', args=[cluster_id])})
    
def create_cluster(req,network_id):
    cluster = Cluster(network = Network.objects.get(id = network_id))
    cluster.save()
    cluster.name = "New cluster %d" % cluster.id
    cluster.save()
    return HttpResponseRedirect(reverse("view_cluster",args=[cluster.id]))
    
def network_inference(req,network_id):
    network = Network.objects.get(id = network_id)
    return direct_to_template(req,"web_bayes/network_inference.html",{"network":network,"graph":inline_svg(VisualiseInferenceNetwork(network,"svg"))},mimetype="application/xhtml+xml")
    
def network_inference_visualisation_svg(req,network_id):
    network = Network.objects.get(id = network_id)
    response = HttpResponse(mimetype='image/svg+xml')
    response['Content-Disposition'] = 'filename=network.svg'
    response.write(VisualiseInferenceNetwork(network,"svg"))
    return response

def toggle_observation(req,state_id):
    print state_id
    state = State.objects.get(id=state_id)
    state.toggle_observed()
    return ok()
    
def perform_inference(req,network_id):
    network = Network.objects.get(id=network_id)
    PerformInference(network)
    return ok()     
    
def clear_inference(req,network_id):
    network = Network.objects.get(id=network_id)
    ClearInference(network)
    return ok()

