import subprocess
from django.core.urlresolvers import reverse

def DotNode(node):
    return '%s [label="%s", style="filled", fontname=Helvetica, fillcolor="lightblue" URL="%s"]' % (node.slug(),node.name,reverse("view_node",args=[node.id]))

def DotEdge(edge):
    return '%s -> %s [ URL="%s"]'%(edge.parent_node.slug(),edge.child_node.slug(),reverse("view_edge",args=[edge.id]))
                
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
        
    for node in network.nodes.filter(cluster=None):
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
    template.append('<TABLE PORT="p0" BGCOLOR="LIGHTBLUE" BORDER="1" CELLBORDER="0" CELLSPACING="1">')
    template.append('<TR><TD COLSPAN="3">')
    template.append(node.name)
    template.append("</TD></TR>")
    
    for state in node.states.all():
        template.append('<TR><TD ALIGN="LEFT">')
        template.append(state.name)    
        template.append("</TD>")        
        template.append('<TD CELLPADDING="1">')        
        template.append('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD WIDTH="%d" BGCOLOR="BLACK"></TD><TD WIDTH="%d"></TD></TR></TABLE>'%(state.probability*50,(1-state.probability)*50))        
        template.append("</TD>")        
        template.append("<TD>%.2f</TD>"%(state.probability))                
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
        
    for node in network.nodes.filter(cluster=None):
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
