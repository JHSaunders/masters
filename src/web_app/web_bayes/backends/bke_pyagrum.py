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
            result = node.get_indexed_value_sets()[0]            
            index = node.get_indexed_value_sets()[1]
            for i in range(len(index)):
                index_dict = {}
                check_dict = {}
                result_i_parents = result[i][0]
                values_i = result[i][1]
                index_i_parents = index[i][0]
                for j in range(len(index_i_parents)):
                    index_dict[result_i_parents[j].node.name] = index_i_parents[j]
                    check_dict[result_i_parents[j].node.name] = result_i_parents[j].name
                G.cpt(node_dict[node.id])[index_dict]=[v.value for v in values_i]
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

