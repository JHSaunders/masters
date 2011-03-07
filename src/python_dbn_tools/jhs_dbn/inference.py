from numpy import *
from numpy.linalg import *

class Slice:
    def __init__(self,time,inference):
        self.time = time
        model = inference.model
        self.inference = inference
        
        self.distributions = {}
        if time>0:
            self.previous = inference.slices[time-1]
        
    def nodes(self):
        for node in self.inference.model["nodes"]:
            yield node
    
    def run(self):
        
        time = self.time
        inference = self.inference
        nodes = self.inference.model["nodes"]
        
        for node in nodes:
            #print node["id"]
            parents = []
            if time == 0:
                for pid in node["inputs"]:
                    parents.append(self.distributions[pid])
            else:
                for pid in node["inputs"]:
                    parents.append(self.distributions[pid])
                if "interslice" in node:
                    for pid in node["interslice"]:
                        parents.append(self.previous.distributions[pid])
            cpt = inference.get_cpt(node["id"],time)
            
            if len(parents)==0:
                dist = cpt
            else:
                dist = matrix([1])
                for parent in parents:
                    dist = kron(dist,parent)
                dist = cpt*dist
            self.distributions[node["id"]] = dist

class SimpleInferenceEngine:
    def __init__(self,model,params):
        self.model = model
        nodes = model["nodes"]
        self.params = params
        model["nodemap"]={}
        for node in nodes:
            model["nodemap"][node["id"]] = node
            for cpd in (node["initial-cpd"],node["cpd"]):
                cpt = matrix(cpd["cpt"])
                cpt.shape = -1,len(node["states"])
                cpt = cpt.T
                cpd["cpt"] = cpt
    
    def get_cpt(self,node,time):
        if time>0:
            return self.model["nodemap"][node]["cpd"]["cpt"]
        else:
            return self.model["nodemap"][node]["initial-cpd"]["cpt"]

    def run(self):
        self.slices = []
        for t in range(self.params["time"]):
            #print "Slice ",t
            s = Slice(t,self)
            s.run()
            self.slices.append(s)
            
       
        results = []
        for s in self.slices:
            p = {}
            for k,v in s.distributions.items():
                d = v.T.tolist()[0]
                p[k] = d
            results.append(p)
            
        return results
