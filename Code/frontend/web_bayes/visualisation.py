import subprocess
from django.core.urlresolvers import reverse

def DotNode(node):
    return '%s [label="%s", style="filled", fillcolor="lightblue" URL="%s"]' % (node.slug(),node.name,reverse("view_node",args=[node.id]))

def DotEdge(edge):
    return '%s -> %s [ URL="%s"]'%(edge.parent_node.slug(),edge.child_node.slug(),reverse("view_edge",args=[edge.id]))
                
def DotBasicNetwork(network):    
    dot = []
    
    dot.append('digraph model{')
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
