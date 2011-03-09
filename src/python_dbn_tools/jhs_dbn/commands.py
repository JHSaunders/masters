#!/usr/bin/python
import sys

from ditto.command import Command,Arg,execute_command,register_command,ValueList
from dbn_processing import *
from inference import SimpleInferenceEngine
from result_viewer import run_viewer

def get_out_stream(name):
    if name =='-' or name==None:
        return sys.stdout
    else:
        return open(name,'w')

def get_in_stream(name):
    if name =='-' or name==None:
        return sys.stdin
    else:
        return open(name,'r')

@register_command
class GenerateCPTSCommand(Command):
    name = "cpts"
    description= "Augments the given model file with CPTs"
    arguments = [ Arg("input","i","The input model ('-' for stdin)",str,default="-"),
                  Arg("output","o","Destination for augmented model('-' for stdout)",str,default="-"),
                  Arg("samples","s","The number of samples to take to calculate a cpd",int,default=10000)]

    def action(self):
        ins = get_in_stream(self.argument_values.input)
        outs = get_out_stream(self.argument_values.output)
        samples = self.argument_values.samples
        if None == samples:
            samples = 10000
        
        r = Random()
        obj = json.load(ins)
        nodes = obj["nodes"]
        prop = obj["properties"]
        setup_node_states(nodes)
        
        node_map = {}
        for node in obj["nodes"]:
            node_map[node["id"]] = node
        
        for node in obj["nodes"]:
            node["shape"] =calculate_shape(node,node_map,["inputs","interslice"])
            node["initial-shape"] =calculate_shape(node,node_map,["inputs"])

            node["cpd"]["cpt"] =calculate_cpt(node,node_map,"cpd",["inputs","interslice"],samples)
            if "initial-cpd" in node:
              node["initial-cpd"]["cpt"] = calculate_cpt(node,node_map,"initial-cpd",["inputs"],samples)
            else:
              node["initial-cpd"] = {}
              node["initial-cpd"] = node["cpd"]
              
        json.dump(obj,outs,indent=4)

@register_command
class GenerateObservationIndexesCommand(Command):
    name = "obs"
    description= "Augments the given parameters file with the indexes of the observations"
    arguments = [ Arg("model","m","The input model ('-' for stdin)",str,default="-"),
                  Arg("parameters","p","The input paramaters ('-' for stdin)",str,default="-"),
                  Arg("output","o","Destination for augmented observations('-' for stdout)",str,default="-")]

    def action(self):
        self.cond_prompt_arg("model")
        self.cond_prompt_arg("parameters")
        
        modelins = get_in_stream(self.argument_values.model)
        parameterins = get_in_stream(self.argument_values.parameters)
        outs = get_out_stream(self.argument_values.output)
        
        model_obj = json.load(modelins)
        param_obj = json.load(parameterins)
        
        set_observation_indexes(model_obj,param_obj)
        json.dump(param_obj,outs,sort_keys=True, indent=4)
        
@register_command
class GraphCommand(Command):
    name = "graph"
    description= "Shows the graph of the given model"
    arguments = [ Arg("input","i","The input model ('-' for stdin)",str,default="-")]
    def action(self):
        ins = get_in_stream(self.argument_values.input)
        show_dot(json.load(ins))

@register_command
class DotCommand(Command):
    name = "dot"
    description= "Print the dot code of the graph of the given network"
    arguments = [ Arg("input","i","The input model ('-' for stdin)",str,default="-"),
                  Arg("output","o","Destination for dot code('-' for stdout)",str,default="-")]
    def action(self):
        ins = get_in_stream(self.argument_values.input)
        outs = get_out_stream(self.argument_values.output)
        outs.write(generate_dot(json.load(ins)))

@register_command
class BarResultsCommand(Command):
    name = "bar"
    description= "Plot a bar chart of the prosterior probabilities of a node after inference"
    arguments = [ Arg("model","m","The model ('-' for stdin)",str,default="-"),
                  Arg("results","r","The results file after inference ('-' for stdin)",str,default="-"),
                  Arg("time","t","The time to look at",int),
                  Arg("node","n","The node to look at"),
                  ]
                  
    def action(self):
        self.prompt_all_args()
        model_ins = get_in_stream(self.argument_values.model)
        results_ins = get_in_stream(self.argument_values.results)
        
        model = json.load(model_ins)
        results = json.load(results_ins)
        bar_result(model,results,self.argument_values.time,self.argument_values.node)

@register_command
class AnimBarResultsCommand(Command):
    name = "abar"
    description= "Plot an animated bar chart of the prosterior probabilities of a node after inference"
    arguments = [ Arg("model","m","The model ('-' for stdin)",str,default="-"),
                  Arg("results","r","The results file after inference ('-' for stdin)",str,default="-"),
                  Arg("node","n","The node to look at"),
                  Arg("fps","f","Frames per second",float),
                  ]
                  
    def action(self):
        self.prompt_all_args()
        model_ins = get_in_stream(self.argument_values.model)
        results_ins = get_in_stream(self.argument_values.results)
        model = json.load(model_ins)
        results = json.load(results_ins)
        anim_bar_result(model,results,self.argument_values.node,self.argument_values.fps)

@register_command
class SimpleInferenceCommand(Command):
    name = "inference"
    description = ""
    arguments = [ Arg("model","m","The input model ('-' for stdin)",str,default="-"),
                  Arg("parameters","p","The input paramaters ('-' for stdin)",str,default="-"),
                  Arg("output","o","Destination for inference results('-' for stdout)",str,default="-")]
                  
    def action(self):
    
        modelins = get_in_stream(self.argument_values.model)
        parameterins = get_in_stream(self.argument_values.parameters)
        
        outs = get_out_stream(self.argument_values.output)
        
        model_obj = json.load(modelins)
        param_obj = json.load(parameterins)
        
        results = SimpleInferenceEngine(model_obj,param_obj).run()
        
        json.dump(results,outs,sort_keys=True, indent=4)

@register_command
class ResultViewerCommand(Command):
    name = "results"
    description = ""
    arguments = [ Arg("model","m","The input model ('-' for stdin)",str,default="model.json"),
                  Arg("parameters","p","The input paramaters ('-' for stdin)",str,default="prm.json"),
                  Arg("results","r","The results file after inference ('-' for stdin)",str,default="res.json"),
                  Arg("auto_update","a","Detect changes inthe model file and automaticaly update",int,default=1) ]
                 
    def action(self):
        if self.argument_values.auto_update == None:
            self.argument_values.auto_update = 1
            
        run_viewer(self.argument_values.model,self.argument_values.parameters,self.argument_values.results,self.argument_values.auto_update)
        
def main():
    execute_command()

if __name__ == "__main__":
    main()
