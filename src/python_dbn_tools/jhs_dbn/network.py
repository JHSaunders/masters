import shutil
import json
from pubsub import Publisher as pub
from collections import OrderedDict

def ordered_hook(pairs):
    """ A simple hook to make the json parser use an OrderedDict """
    d = OrderedDict()
    for p in pairs:
        d[p[0]]=p[1]
    return d

class Network():
    def __init__(self, filename):
        self.filename = filename
        shutil.copy(filename,filename+"~") #make a backup
        
        with open(filename) as f:
            json_loaded = json.load(f)
        
        self.name = json_loaded["properties"]["name"]
        self.type = json_loaded["properties"]["type"]
        
        nodes_loaded = json_loaded["nodes"]
        self.nodes = []
        for node_dict in nodes_loaded:
            node = Node(self,node_dict)
            self.nodes.append(node)
        
    
    def save(self):
        store_dict = OrderedDict()
        store_dict["properties"] = {}
        store_dict["properties"]["name"] = self.name
        store_dict["properties"]["type"] = self.type
        
        store_dict["nodes"] = []
        for node in self.nodes:
            store_dict["nodes"].append(node.save())
        
        with open("new_"+self.filename,'w') as f:
            json.dump(store_dict,f,indent=2)
    
    def get_node(self,id):
        for node in self.nodes:
            if node.id() == id:
                return node
        return None
    
    def add_node(self):
        node = Node(self)
        id = "new_node"
        ctr = 1
        while self.get_node(id)!=None:
            id = "new_node({0})".format(ctr)
            ctr+=1
        node.id(id)
        self.nodes.append(node)
        pub.sendMessage("node_added", {"node":node})
        return node
    
    def remove_node(self,node):
        if not node is None:
            self.nodes.remove(node)
            pub.sendMessage("node_removed", {"node":node})
    
    def generate_dot(self):
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
                
        def cpd_label(cpd):
            if cpd.distribution()!="":
                return cpd.distribution()
            else:
                return cpd.expression()
            
        p = Printer()
                
        p.write("digraph {0} {{".format(self.name.replace(" ","_")))
        p.push()
        p.write("rankdir=BT")
        
        clusters = set([""])
        for node in self.nodes:
            clusters.add(node.cluster())
                    
        for cluster in clusters:        
            if cluster!="":
                p.write("subgraph cluster_{0}{{\n".format(cluster.replace(" ","_")))
                p.push()
                p.write("label=\"{0}\"".format(cluster))
                p.write("fontsize=28")
                
            for node in self.nodes:
               
                if cluster!=node.cluster():
                    continue
                
                p.write('"'+node.id()+"\" [")
                p.push()
                
                label = "{5}\\n[{0}:{1}:{2}]\\n{3}={4}".format(node.range()[0],node.interval(),node.range()[1],node.id(),cpd_label(node.cpd()),node.label())
                if cpd_label(node.initial_cpd()) !="":
                    label += "\\n({0}={1})".format(node.id(),cpd_label(node.initial_cpd()))
                
                url = node.id()
                p.write("label = \"{0}\",".format(label))
                p.write('URL = "{0}"'.format(url))
                
                is_driver = len(node.inputs())+len(node.interslice()) == 0
                is_retrospective = len(node.interslice())>0
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
                
        for node in self.nodes:
            for input in node.inputs():
                p.write("\"{0}\"->\"{1}\"".format(input,node.id()))
        
        for node in self.nodes:
            for input in node.interslice():
                p.write('\"{0}\"->\"{1}\"[constraint=false, color="blue", style="dashed"]'.format(input,node.id()))

        p.pop()
        p.write("}")
        return p.dot_str

class SchemaLoadedObject(object):
    def __init__(self,parent,key):
        self.parent = parent
        self.key = key
    
    def on_change(self,key):
        self.parent.child_changed(self,key)
    
    def child_changed(self,child,key):
        self.on_change(child.key+"."+key)
        
    def create_mutator(self,key):
        self.mutators.append(key)
        def fn(value = None,autosave=True):
            data_k = "__data_"+key
            if value != None and getattr(self,data_k) != value:
                setattr(self,data_k,value)
                self.on_change(key)
            return getattr(self,data_k)
        return fn
        
    def create_child(self,key):        
        self.children.append(key)
        def fn(value = None):
            data_k = "__data_"+key
            return getattr(self,data_k)
        return fn
        
    def create_from_schema(self,schema_dict):
        self.children = []
        self.mutators = []                
        for k,v in schema_dict.items():
             data_k = "__data_"+k
             if not isinstance(v,OrderedDict): 
                setattr(self,data_k,v)
                setattr(self,k,self.create_mutator(k))
             else:
                child = SchemaLoadedObject(parent = self,key = k)
                child.create_from_schema(v)
                setattr(self,data_k,child)
                setattr(self,k,self.create_child(k))
        
    def load(self,json):
        for k,v in json.items():
            if k in self.mutators:
                getattr(self,k)(v,False)
            elif k in self.children:
                getattr(self,k)().load(v)
            
    def save(self):
        store_dict = OrderedDict()
        for k in self.mutators:
            store_dict[k] = getattr(self,k)()
        for k in self.children:
            store_dict[k] = getattr(self,k)().save()
        return store_dict

node_schema = """{
            "id": "",
            "cluster":"",
            "label": "",
            "description": "",
            "inputs":[],
            "interslice":[],
            "range":[0,1],
            "interval":1,
            "infinities":false,
            "cpd":{
                "expression":"",
                "distribution":""                
                },
            "initial_cpd":{
                "expression":"",
                "distribution": ""
                }
        }"""

class Node(SchemaLoadedObject):
    def __init__(self, network,json_dict={}):        
        self.loaded = False
        self.network = network
        schema_dict = json.loads(node_schema,object_pairs_hook = ordered_hook)
        self.create_from_schema(schema_dict)
        self.load(json_dict)
        self.loaded = True
    
    def on_change(self,key):
        if self.loaded:
            self.network.save()
            pub.sendMessage("node_changed", {"node":self, "key":key})
        
