#!/usr/bin/python
import json
import sys

tab_stop = 0

def pprint(str):
    tabs=""
    for i in range(tab_stop):
        tabs+="    "
    print(tabs+str)

def ppush():
    global tab_stop
    tab_stop+=1
    
def ppop():
    global tab_stop
    tab_stop-=1
    
input_file = open(sys.argv[1])
obj = json.load(input_file)
nodes = obj["nodes"]
prop = obj["properties"]


pprint("class {0} {{".format(prop["name"]))
ppush()
for node in obj["nodes"]:
    pprint("node "+node["id"]+" {")
    ppush()
    pprint("label = \"{0}\";".format(node["label"]))
    pprint("subtype = interval;")

    state_values = map(str, range(node["range"][0],node["range"][1],node["interval"])+[node["range"][1]])
    if node["infinities"]:
        state_values.insert(0,"-infinity")
        state_values.append("infinity")

    states = map(lambda x: "\"\"",range(len(state_values)-1))

    pprint("states = ({0});".format(" ".join(states)))
    pprint("state_values = ({0});".format(" ".join(state_values)))
    ppop()
    pprint("}\n")
    
for node in obj["nodes"]:
    pot_exp = node["id"]
    if len(node["inputs"])>0:
        pot_exp += " | " + " ".join(node["inputs"])
    pprint("potential ( {0} ) {{".format(pot_exp))
    ppush();
    pprint("model_nodes = ();")
    pprint("model_data = ( {0} );".format(node["expression"]))
    ppop();
    pprint("}\n")
ppop()
pprint("}")
