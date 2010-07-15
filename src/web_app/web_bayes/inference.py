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
