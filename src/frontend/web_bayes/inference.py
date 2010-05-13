from backends.bke_openbayes import PerformOpenBayesInference

def PerformInference(network):
    PerformOpenBayesInference(network)
    
def ClearInference(network):
    for node in network.nodes.all():
        for state in node.states.all():
            state.inferred_probability = None
            state.observed = False
            state.save()
