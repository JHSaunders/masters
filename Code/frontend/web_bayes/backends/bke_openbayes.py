from OpenBayes import BNet, BVertex, DirEdge
from OpenBayes import JoinTree, MCMCEngine
def PerformOpenBayesInference(network):    
    G = BNet( network.name )
    
    node_dict = {}

    for node in network.nodes.all():
       pynode =  BVertex( node.name, True, node.states.count() )
       node_dict[node.id] = pynode
       G.add_v(pynode)

    for edge in network.edges.all():
        pyedge = DirEdge( len( G.e ),node_dict[edge.parent_node.id] , node_dict[edge.child_node.id])
        G.add_e( pyedge )    

    print G

    G.InitDistributions()
    
    for node in network.nodes.all():
        if not node.is_root():        
            result = node.get_indexed_value_sets()[0]            
            index = node.get_indexed_value_sets()[1]
            for i in range(len(index)):
                index_dict = {}
                result_i_parents = result[i][0]
                values_i = result[i][1]
                index_i_parents = index[i][0]
                for j in range(len(index_i_parents)):
                    index_dict[result_i_parents[j].node.name] = index_i_parents[j]
                node_dict[node.id].distribution[index_dict] = [v.value for v in values_i] 
        else:
            node_dict[node.id].setDistributionParameters([state.probability for state in node.states.all()])
        print node_dict[node.id].distribution
    
    #ie = JoinTree(G)
    ie = MCMCEngine(G)
    
    # perform inference with no evidence
    results = ie.MarginaliseAll() 
    
    for node_name, distribution in results.items():
        node = network.nodes.get(name=node_name)        
        i=0    
        for state in node.states.all():
            state.probability = distribution[i]
            state.save()
            i+=1
        
