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


from OpenBayes import BNet, BVertex, DirEdge,SaveXBN
from OpenBayes import JoinTree, MCMCEngine

def CreateOpenBayesNetwork(network):
    G = BNet( network.name )
    
    node_dict = {}

    for node in network.nodes.all():
       pynode =  BVertex( node.name, True, node.states.count() )
       node_dict[node.id] = pynode
       G.add_v(pynode)

    for edge in network.edges.all():
        pyedge = DirEdge( len( G.e ),node_dict[edge.parent_node.id] , node_dict[edge.child_node.id])
        G.add_e( pyedge )    

    G.InitDistributions()

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
                     
                node_dict[node.id].distribution[index_dict] = [v.value for v in values_i]                 
            print "\n"    
        else:
            node_dict[node.id].setDistributionParameters([state.probability for state in node.states.all()])

    return (G,node_dict)

def PerformOpenBayesInference(network,alg):

    (G,node_dict) = CreateOpenBayesNetwork(network)           
    if alg=="jt":    
        ie = JoinTree(G)
    else:
        ie = MCMCEngine(G)
    
    obs_dict={}
    for node in network.nodes.all():
        i = 0
        for state in node.states.all():
            if state.observed:
                obs_dict[node.name]=i
            i+=1
    ie.SetObs(obs_dict)
    results = ie.MarginaliseAll() 
        
    for node_name, distribution in results.items():
        node = network.nodes.get(name=node_name)        
        i=0    
        print node_dict[node.id].distribution
        for state in node.states.all():
            state.inferred_probability = distribution[i]
            if state.inferred_probability is None or math.isnan(state.inferred_probability):
                state.inferred_probability = None
            state.save()
            
            i+=1

def ExportToXBN(network):
    (G,node_dict) = CreateOpenBayesNetwork(network)
    SaveXBN('network.xbn.tmp~',G)
    f = open('network.xbn.tmp~','r')
    output = []
    for line in f:
        output.append(line)
    f.close();
    
    return '\n'.join(output)
