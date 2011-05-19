import csv 
from load_graph import G
import networkx as nx

reader = csv.reader(open("index.csv"))

clusters = {}
for row in reader:
    id = row[0]    
    cluster = ""
    if len(row)>2:
        cluster = row[2]
    
    if cluster not in clusters:
        clusters[cluster] = []

    clusters[cluster].append(id)
    
print "digraph {"
print '  ranksep="3.0"'
print '  concentrate=true'
print '  fontname="Arial"'
for k,v in clusters.items():
    if not (k=="" or "areas" in k ):#or "reality" in k):
        print "\n  subgraph cluster_{0}{{".format(k)
        print '    label="{0}"'.format(k.replace('_',' ').capitalize())
        print '    style="filled"'
        print '    fillcolor=lightblue'

    for node in v:
        label = G.node[node]["label"]
        print '    {0}[label="{1}",style=filled,fillcolor="white"]'.format(node,label)
    if not (k=="" or "areas" in k ):#or "reality" in k):
        print "  }"
        
for edge in G.edges():
    print "  {0}->{1}".format(edge[0],edge[1])
print "}"
