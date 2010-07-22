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
import math
import pyAgrum
from pyAgrum import BayesNet, LabelizedVar, LazyPropagation, Gibbs

def PerformPyAgrumInference(network,alg):
    G = BayesNet( str(network.name) )
    
    node_dict = {}

    for node in network.nodes.all():
        pynode =  G.add(LabelizedVar( str(node.name), str(node.name), node.states.count()))
        node_dict[node.id] = pynode
           
    for edge in network.edges.all():
        p = node_dict[edge.parent_node.id]
        c = node_dict[edge.child_node.id]
        G.insertArc(p,c)
    
   
    for node in network.nodes.all():
        if not node.is_root():
            rows = node.CPT().get_cpt_rows()
            index_dict = {}
            for row in rows:
                i = 0
                for parent in node.parent_nodes():
                    index_dict[parent.name]= row[0][i]
                    i+=1
                G.cpt(node_dict[node.id])[index_dict]=list(row[1])
                #print index_dict,rows[1]
        else:
            G.cpt(node_dict[node.id]).fillWith([state.probability for state in node.states.all()])          
    if alg=="gibbs":    
        ie = Gibbs(G)
    else:
        ie = LazyPropagation(G)

    obs_dict={}
    for node in network.nodes.all():
        i = 0
        for state in node.states.all():
            if state.observed:
                obs_dict[node.name]=i
            i+=1
    ie.setEvidence(obs_dict)
    ie.makeInference() 
        
    for node in network.nodes.all():
        distribution = ie.marginal(node_dict[node.id])       
        i=0    
        for state in node.states.all():
            state.inferred_probability = distribution[i]
            if math.isnan(state.inferred_probability):
                state.inferred_probability = None
            state.save()            
            i+=1

