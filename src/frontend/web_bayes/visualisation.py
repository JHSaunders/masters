from xml.dom.minidom import parse, parseString

import subprocess

from django.core.urlresolvers import reverse

def inline_svg(xml):
    dom = parseString(xml)
    return dom.documentElement.toxml()

color = {'C':"lightblue",'A':"red",'U':"yellow"}
shape = {'C':"ellipse",'A':"rectangle",'U':"diamond"}

edge_style = {'R':'solid','I':'solid','E':'dashed','IE':'dashed'}
edge_arrow = {'R':'normal','I':'diamond','E':'normal','IE':'diamond'}

def DotNode(node):
    return '%s [label="%s", style="filled", fontname=Helvetica, fillcolor="%s",shape="%s", URL="%s"]' % (node.slug(),node.name,color[node.node_class],shape[node.node_class],reverse("view_node",args=[node.id]))

def DotEdge(edge):
    label = edge.edge_effect
    if label == None:
        label = ""
    return '%s -> %s [ URL="%s", arrowhead=%s, style=%s,label="%s"]'%(edge.parent_node.slug(),edge.child_node.slug(),reverse("view_edge",args=[edge.id]),edge_arrow[edge.edge_class],edge_style[edge.edge_class],label)
                
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
        dot.append('URL="%s";' % (reverse("view_cluster",args=[cluster.id]),))
        
        for node in cluster.nodes.all():
            dot.append(DotNode(node))
        dot.append('}')
        
    for node in network.free_nodes:
        dot.append(DotNode(node))
    
    for edge in network.edges.all():
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

def DotInferenceNode(node):
    template = []
    values = []
    template.append("<")
    template.append('<TABLE PORT="p0" BGCOLOR="%s" BORDER="1" CELLBORDER="0" CELLSPACING="1">' % (color[node.node_class]))
    template.append('<TR><TD COLSPAN="3">')
    template.append(node.name)
    template.append("</TD></TR>")
    
    for state in node.states.all():
        toggle_url = reverse('toggle_observation',args=[state.id])
        
        template.append('<TR><TD ALIGN="LEFT" HREF="%s" TOOLTIP="Click to set observation">'%(toggle_url))
        template.append(state.name)
        template.append("</TD>")
        
        
        template.append('<TD CELLPADDING="1" HREF="%s" TOOLTIP="Click to set observation">'%(toggle_url))
        if not node.is_observed() and state.inferred_probability != None: 
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
    return '%s [label=%s, fontname=Helvetica, shape=plaintext]' % (node.slug(),html)

def DotInferenceEdge(edge):
    return '%s:p0 -> %s:p0 '%(edge.parent_node.slug(),edge.child_node.slug())

def DotInferenceNetwork(network):    
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
        
        for node in cluster.nodes.all():
            dot.append(DotInferenceNode(node))
        dot.append('}')
        
    for node in network.free_nodes:
        dot.append(DotInferenceNode(node))
    
    for edge in network.edges.all():
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
