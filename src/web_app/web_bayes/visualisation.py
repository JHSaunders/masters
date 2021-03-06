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
from xml.dom.minidom import parse, parseString

import subprocess
import urllib

from django.core.urlresolvers import reverse
from models import *
def inline_svg(xml):
    dom = parseString(xml)
    return dom.documentElement.toxml()

color = {'C':"lightblue",'A':"red",'U':"yellow"}
shape = {'C':"ellipse",'U':"rectangle",'A':"diamond"}

edge_style = {'R':'solid','I':'solid','E':'dashed','IE':'dashed'}
edge_arrow = {'R':'normal','I':'diamond','E':'normal','IE':'diamond'}

def DotNode(node):
    return '%s [label="%s", style="filled", fontname=Helvetica, fillcolor="%s",shape="%s", URL="javascript: network_graph.open_form(\'%s\')"]' % (node.id,node.name.replace(" ","\\n"),color[node.node_class],shape[node.node_class],reverse("view_node",args=[node.id]))

def DotEdge(edge):
    label = edge.edge_effect
    if label == None:
        label = ""
    return '%s -> %s [ URL="javascript: network_graph.open_form(\'%s\')", arrowhead=%s, style=%s,label="%s"]'%(edge.parent_node.id,edge.child_node.id,reverse("view_edge",args=[edge.id]),edge_arrow[edge.edge_class],edge_style[edge.edge_class],label)
                
def DotBasicNetwork(network):
    dot = []
    
    dot.append('digraph model{')
    dot.append('fontname=Helvetica')
    dot.append('bgcolor=transparent')
    id_cluster = 0
    for cluster in network.clusters.all():
        id_cluster +=1
        dot.append('subgraph cluster_%s{'%(id_cluster,))
        dot.append('label="%s";' % (cluster.name,))
        dot.append('bgcolor="%s";' % ("aliceblue",))
        dot.append('URL="javascript: network_graph.open_form(\'%s\')";' % (reverse("view_cluster",args=[cluster.id]),))
        
        for node in cluster.nodes.all():
            dot.append(DotNode(node))
        dot.append('}')
        
    for node in network.free_nodes:
        dot.append(DotNode(node))
    
    for edge in network.edges.select_related().all():
        dot.append(DotEdge(edge))
        
    dot.append('}')
    
    dot_str = '\n'.join(dot)

    return dot_str

def VisualiseBasicNetwork(network,format):    
    dot_string = DotBasicNetwork(network)
    p = subprocess.Popen('/usr/bin/dot -T%s'%format, shell=True,\
    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout,stderr) = p.communicate(dot_string)
    return stdout

def DotInferenceNode(node,states):
    def is_node_observed(states):
        for state in states:
            if state.observed:
                return True
        return False       
             
    template = []
    values = []
    template.append("<")
    template.append('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="1">')
    template.append('<TR><TD COLSPAN="3">')
    template.append(node.name.replace('&','&amp;'))
    template.append("</TD></TR>")
    
    is_observed = is_node_observed(states)
    for state in states:
        toggle_url = "javascript:network_graph.send_and_refresh('%s')"%reverse('toggle_observation',args=[state.id])
        
        template.append('<TR><TD ALIGN="LEFT" HREF="%s" TOOLTIP="Click to set observation">'%(toggle_url))
        template.append(state.name+"&nbsp;")
        template.append("</TD>")
        
        
        template.append('<TD CELLPADDING="1" HREF="%s" TOOLTIP="Click to set observation">'%(toggle_url))
        if not is_observed and state.inferred_probability != None: 
            template.append('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD WIDTH="%d" BGCOLOR="BLACK"></TD><TD WIDTH="%d"></TD></TR></TABLE>'%(state.inferred_probability*50,(1-state.inferred_probability)*50))
            template.append("</TD>")
            template.append('<TD HREF="%s" TOOLTIP="Click to set observation">%.2f</TD>'%(toggle_url,state.inferred_probability))
        elif state.observed:
            template.append('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD WIDTH="50" BGCOLOR="GREEN"></TD></TR></TABLE>')
            template.append("</TD>")
            template.append('<TD HREF="%s" TOOLTIP="Click to set observation">%.2f</TD>'%(toggle_url,1))
        else:
            template.append('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD WIDTH="50" ></TD></TR></TABLE>')
            template.append("</TD>")
            template.append('<TD HREF="%s" TOOLTIP="Click to set observation"></TD>'%(toggle_url))                
        template.append("</TR>")
        
    template.append("</TABLE>")
    template.append(">")
    html = "".join(template)
    return '%s [label=%s, fillcolor=%s, fontname=Helvetica, shape=box, style="rounded,filled"]' % (node.id,html,color[node.node_class])

def DotInferenceEdge(edge):
    return '%s -> %s '%(edge.parent_node.id,edge.child_node.id)

def DotInferenceNetwork(network):
    dot = []
    
    all_network_states = State.objects.select_related().filter(node__network = network).all()  
    network_states = {}
    for state in all_network_states:
        if state.node.id not in network_states:
             network_states[state.node.id] = []
        network_states[state.node.id].append(state)
        
    dot.append('digraph model{')
    dot.append('fontname=Helvetica')
    dot.append('bgcolor=transparent')
    id_cluster = 0
    for cluster in network.clusters.all():
        id_cluster +=1
        dot.append('subgraph cluster_%s{'%(id_cluster,))
        dot.append('label="%s";' % (cluster.name,))
        dot.append('bgcolor="%s";' % ("aliceblue",))
        
        for node in cluster.nodes.all():
            
            dot.append(DotInferenceNode(node,network_states.get(node.id,[])))
        dot.append('}')
      
    for node in network.free_nodes:
        dot.append(DotInferenceNode(node,network_states.get(node.id,[])))
    
    for edge in network.edges.select_related().all():
        dot.append(DotInferenceEdge(edge))
        
    dot.append('}')
    
    dot_str = '\n'.join(dot)

    return dot_str
    
def VisualiseInferenceNetwork(network,format):    
    dot_string = DotInferenceNetwork(network)
    p = subprocess.Popen('/usr/bin/dot -T%s'%format, shell=True,\
    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout,stderr) = p.communicate(dot_string)
    return stdout
