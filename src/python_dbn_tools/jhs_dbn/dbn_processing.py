#!/usr/bin/python
import json
import sys
from random import Random
from scipy.stats import *
from xdot import *
import gtk
from math import *

r = Random()

def intervals(start,stop,step):
    p = start
    n = start
    r = []
    while p<stop:
      n = round(min(p+step,stop),2)
      r.append((p,n))
      p = n
    return r

def eval_exp(inputs,expr):
    def Normal(mu,sigma):
        return r.gauss(mu,sigma)
    normal = Normal
    gauss = Normal
    
    def rand():
        return r.random()
        
    for k,v in inputs.items():
        expr = expr.replace(k,str(v))
    return eval(expr)

def eval_exp_on_range(input_intervals,expr,output_intervals,num_samples):
    counts = [0 for i in output_intervals]
    
    def find_interval(value,intervals):
        if value <= intervals[0][0]:
            return 0
            
        for i in range(len(intervals)):
            if intervals[i][0]<=value and value < intervals[i][1]:
                return i
                
        if value >= intervals[-1][1]:
            return len(intervals)-1
        
    def normalize_counts(counts):
        total = sum(counts)
        return map(lambda x: float(x)/total,counts)    
        
    for q in range(num_samples):
        input_values = dict((k,(q/float(num_samples))*(i[1]-i[0])+i[0]) for k,i in input_intervals.items())
        result = eval_exp(input_values,expr)

        i = find_interval(result,output_intervals)
        counts[i]+=1
    return normalize_counts(counts)

def pprint_cpt(parents,inputs_states,combinations,output_states,original_cpt):
    cpt = original_cpt[:]
    lines = []
    
    input_col_size = reduce(max,map(len,parents),9)
    output_col_size = max(reduce(max,map(len,map(str,output_states))),4)
    
    input_state_labels = map(lambda x:("{0:^"+str(input_col_size)+"}").format(x), parents)
    output_state_labels = map(lambda x:("{0:^"+str(output_col_size)+"}").format(x), output_states)
    
    line = "| "+" | ".join(input_state_labels)+" || " + " | ".join(output_state_labels) +" |"
    lines.append(line)    
    
    for combo in combinations:
        input_states = [inputs[x][combo[x]] for x in range(len(combo))]
        values = cpt[:len(output_states)]
        cpt = cpt[len(output_states):]
        
        input_state_labels = map(lambda x:("{0:^"+str(input_col_size)+"}").format(x), map(lambda x: "({0:0.1f},{1:0.1f})".format(x[0],x[1]),input_states))
        value_labels = map(lambda x:("{0:^"+str(output_col_size)+"}").format(x), map(lambda x: "" if x==0 else int(x*100),values))
        line = "| "+" | ".join(input_state_labels)+" || " + " | ".join(value_labels) + " |"
        lines.append(line)
    
    return "\n".join(lines)

def setup_node_states(nodes):
    for node in nodes:
        id = node["id"]
        states = intervals(node["range"][0],node["range"][1],node["interval"])
        if node["infinities"]:
            states.insert(0,(float("-infinity"),states[0][0]))
            states.append((states[-1][1],float("-infinity")))
        node["states"] = states

def calculate_shape(node,node_map,input_fields):
  inputids = []
  for field in input_fields:
    if field in node:
      for inputid in node[field]:
            inputids.append(inputid)
  inputids.append(node["id"])
  return map(lambda x: len(node_map[x]["states"]),inputids)

def calculate_cpt(node,node_map,cpd_field,input_fields,num_samples):
    cpd = node[cpd_field]
    if "distribution" in cpd:
        return calculate_cpt_distribution(node,node_map,cpd_field,input_fields,num_samples)
    elif "expression" in cpd:
        return calculate_cpt_expression(node,node_map,cpd_field,input_fields,num_samples)

def calculate_cpt_distribution(node,node_map,cpd_field,input_fields,num_samples):
    cpd = node[cpd_field]
    rv = eval(cpd["distribution"])
    states = node["states"]
    cpt = []
    for [s,e] in states:
        prob = rv.cdf(e)-rv.cdf(s)
        cpt.append(prob)
    total = sum(cpt)
    cpt = map(lambda x: x/total,cpt)
    return cpt

def calculate_cpt_expression(node,node_map,cpd_field,input_fields,num_samples):
    id = node["id"]
    inputs = []
    inputids = []
    
    for field in input_fields:
        if field in node:
            for inputid in node[field]:
                inputids.append(inputid)

    inputs =[node_map[inputid]["states"] for inputid in inputids]
    
    combinations = []
    
    indexes = [0 for x in range(len(inputs))]

    total_states = 1 
    
    for input in inputs:
        total_states*=len(input)

    while len(combinations)<total_states:
        combinations.append([x for x in indexes])
        for j in range(1,len(inputs)+1):
            i = len(inputs)-j
            indexes[i]+=1
            if indexes[i]==len(inputs[i]):
                indexes[i] = 0
            else:
                break
    output_states = node["states"]
    cpt = []

    for combo in combinations:
        input_states = dict((inputids[x],inputs[x][combo[x]]) for x in range(len(combo)))
        cpt+=eval_exp_on_range(input_states,node[cpd_field]["expression"],output_states,num_samples)
    return cpt

def set_observation_indexes(model_obj,param_obj):
    nodes = model_obj["nodes"]
    prop = model_obj["properties"]

    node_map = {}
    for node in nodes:
        node_map[node["id"]] = node
    
    setup_node_states(nodes)
    
    observations = param_obj["observations"]
    observation_indexes = {}
    for t,ob in observations.items():
        obs_idx = {}
        for k,v in ob.items():
            i = 0
            for s in node_map[k]["states"]:
                if s[0]<=v<=s[1]:
                    obs_idx[k]=i
                    break
                i+=1
        observation_indexes[t] = obs_idx

    param_obj["observations_by_index"] = observation_indexes

def generate_dot(model):
    class Printer:
        tab_stop = 0
        dot_str = ""

        def write(self,str):
            tabs=""
            for i in range(self.tab_stop):
                tabs+="    "
            self.dot_str+=tabs+str+"\n"

        def push(self):
            self.tab_stop+=1

        def pop(self):
            self.tab_stop-=1

    p = Printer()
    
    obj = model
    nodes = obj["nodes"]
    prop = obj["properties"]
    
    p.write("digraph {0} {{".format(prop["name"].replace(" ","_")))
    p.push()
    p.write("rankdir=BT")
    
    clusters = set([""])
    for node in obj["nodes"]:
        if "cluster" in node:
            clusters.add(node["cluster"])
    
    for cluster in clusters:
    
        if cluster!="":
            p.write("subgraph cluster_{0}{{\n".format(cluster.replace(" ","_")))
            p.push()
            p.write("label=\"{0}\"".format(cluster))
            p.write("fontsize=28")
            
        for node in obj["nodes"]:
            node_cluster = ""
            if "cluster" in node:
                node_cluster = node["cluster"]
            
            if cluster!=node_cluster:
                continue
            
            p.write(node["id"]+" [")
            p.push()
            
            def get_expr_label(cpd):
                expr = "?"
                if "expression" in cpd:
                    expr = cpd["expression"]
                elif "distribution" in cpd:
                    expr = cpd["distribution"]
                return expr
            
            label = node["label"]+"\\n"+"[{0}:{1}:{2}]\\n".format(node["range"][0],node["interval"],node["range"][1])+node["id"]+"="+get_expr_label(node["cpd"])
            if "initial-cpd" in node:
                label += "\\n("+node["id"]+"="+get_expr_label(node["initial-cpd"])+")"
            
            url = node["id"]
            p.write("label = \"{0}\",".format(label))
            p.write('URL = "{0}"'.format(url))
            
            if not ("interslice" in node):
                node["interslice"] = []
                
            is_driver = len(node["inputs"])+len(node["interslice"]) == 0
            is_retrospective = len(node["interslice"])>0
            if is_driver:
                p.write("style=filled")
                p.write("color=orange")
            if is_retrospective:
                p.write("style=filled")
                p.write("color=lightblue")
            p.pop()
            p.write("]\n")
        
        if cluster!="":
            p.write("}\n")
            p.pop()
            
    for node in obj["nodes"]:
        for input in node["inputs"]:
            p.write("{0}->{1}".format(input,node["id"]))
    for node in obj["nodes"]:
        if "interslice" in node:
            for input in node["interslice"]:
                p.write('{0}->{1}[constraint=false, color="blue", style="dashed"]'.format(input,node["id"]))

    p.pop()
    p.write("}")
    return p.dot_str

def show_dot(model):
    win = DotWindow()
    win.connect('destroy', gtk.main_quit)
    win.set_dotcode(generate_dot(model))
    gtk.main()

def bar_result(model,result,time,node_name):
    import matplotlib.pyplot as plt
    setup_node_states(model["nodes"])
    for n in model["nodes"]:
        if n["id"] == node_name:
            node = n
            break
    left = map(lambda x: x[0],n["states"])
    width = map(lambda x: x[1] - x[0],n["states"])
    plt.bar(left,result[time][node_name],width)
    plt.xlim(left[0],left[-1]+width[-1])
    plt.ylim(0,1)
    plt.title("{0} ({1}) at t={2}".format(node["label"],node["id"],time))
    plt.draw()
    plt.show()

def anim_bar_result(model,result,node_name,fps):
    import time
    import numpy as np
    import matplotlib
    matplotlib.use('GTKAgg') # do this before importing pylab
    import matplotlib.pyplot as plt
    
    setup_node_states(model["nodes"])
    for n in model["nodes"]:
        if n["id"] == node_name:
            node = n
            break
    left = map(lambda x: x[0],n["states"])
    width = map(lambda x: x[1] - x[0],n["states"])

    fig = plt.figure()

    ax = fig.add_subplot(111)    

    def animate():
        t=0
        for sl in result:
           ax.cla()
           ax.bar(left,sl[node["id"]],width)
           ax.set_ylim(0,1)
           ax.set_xlim(left[0],left[-1]+width[-1])
           plt.title("{0} ({1}) at t={2}".format(node["label"],node["id"],t))
           fig.canvas.draw()                         # redraw the canvas
           time.sleep(1.0/fps)
           t+=1
    import gobject
    gobject.idle_add(animate)
    plt.show()

def load_results():
    model = json.load(open("model.json","r"))
    res = json.load(open("res.json","r"))
    return (model,res)

##    fig = Figure(figsize=(4,4))
##    ax = fig.add_subplot(111)
##    ax.bar(left,result[0][node_name],width)
##    fig.show()
#    from pylab import *
#    import time
#    ion()
#    
#    line, = plot(left,result[0][node_name])
#    for tslice in result:
#        line.set_ydata(tslice[node_name])  # update the data        
#        draw()                         # redraw the canvas
#        time.sleep(1)
