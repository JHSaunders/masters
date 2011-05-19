import csv 
from load_graph import G
import networkx as nx

w = csv.writer(open("index.csv",'w'))

for t in G.nodes(data=True):
    label = t[1]['label']
#    label = label[:label.find(r'\n')]
    w.writerow((t[0],label))
    
