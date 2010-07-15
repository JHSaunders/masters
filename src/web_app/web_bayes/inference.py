from backends.bke_openbayes import PerformOpenBayesInference
try:
    from backends.bke_pyagrum import PerformPyAgrumInference
    has_pyAgrum=True
except:
    has_pyAgrum=False
    
def PerformInference(network):
    for node in network.nodes.all():
        node.normalise_node()
    
    if network.backend == 'openbayes-jt':
        PerformOpenBayesInference(network, alg='jt')
    elif network.backend == 'openbayes-mcmc':
        PerformOpenBayesInference(network, alg='mcmc')
    elif network.backend == 'agrum-lazy' and has_pyAgrum:
        PerformPyAgrumInference(network,alg='lazy')
    elif network.backend == 'agrum-gibbs' and has_pyAgrum:
        PerformPyAgrumInference(network,alg='gibbs')
        
def ClearInference(network):
    for node in network.nodes.all():
        for state in node.states.all():
            state.inferred_probability = None
            state.observed = False
            state.save()
