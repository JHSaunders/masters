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

def PerformOpenBayesInference(network):

    (G,node_dict) = CreateOpenBayesNetwork(network)           

    ie = JoinTree(G)
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
            if state.probability is None or math.isnan(state.probability):
                state.inferred_probability = -1 
            state.observed=False
            state.save()
            
            i+=1

def ExportToXBN(network):
    (G,node_dict) = CreateOpenBayesNetwork(network)
    SaveXBN('temp.xbn',G)
    f = open('temp.xbn','r')
    output = []
    for line in f:
        output.append(line)
    f.close();
    
    return '\n'.join(output)
