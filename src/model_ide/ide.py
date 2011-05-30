#!/usr/bin/env python

import json
import pygtk
pygtk.require('2.0')
import gtk

from collections import OrderedDict

from pubsub import Publisher as pub

import xdot

class Network:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            json_loaded = json.load(f)
            
        nodes_loaded = json_loaded["nodes"]
        self.nodes = []
        for node_dict in nodes_loaded:
            node = Node(self,node_dict)
            self.nodes.append(node)
        
        self.name = json_loaded["properties"]["name"]
        self.type = json_loaded["properties"]["type"]
        self.save()
        
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
                
                label = "{3}\\n[{0}:{1}:{2}]\\n{3}={4}".format(node.range()[0],node.interval(),node.range()[1],node.id(),node.cpd())
                if str(node.initial_cpd())!="":
                    label += "\\n({0}={1})".format(node.id(),node.initial_cpd())
                
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

def ordered_hook(pairs):
    d = OrderedDict()
    for p in pairs:
        d[p[0]]=p[1]
    return d
    
class Node:
    def __init__(self, network,json={}):
        self.network = network
        self.create_from_schema(node_schema)
        self.load(json)
        
    def create_mutator(self,key):
        self.mutators.append(key)
        def fn(value = None,autosave=True):
            data_k = "__node_data_"+key
            if value != None and getattr(self,data_k) != value:
                setattr(self,data_k,value)
                if autosave:
                    self.network.save()
                pub.sendMessage("node_changed", {"node":self, "key":key})
            return getattr(self,data_k)
        return fn
    
    def create_accessor(self,key):
        self.accessors.append(key)
        def fn(value = None):
            data_k = "__node_data_"+key
            return getattr(self,data_k)
        return fn
    
    def create_from_schema(self,schema):
        self.accessors = []
        self.mutators = []
        schema_dict = json.loads(schema,object_pairs_hook = ordered_hook)
        for k,v in schema_dict.items():
             data_k = "__node_data_"+k
             if k!= "cpd" and k!="initial_cpd":
                setattr(self,data_k,v)
                setattr(self,k,self.create_mutator(k))
             else:
                cpd = CPD(self,v,k)
                setattr(self,data_k,cpd)
                setattr(self,k,self.create_accessor(k))
    
    def load(self,json):
        for k,v in json.items():
            if k in self.mutators:
                getattr(self,k)(v,False)
            elif k in self.accessors:
                getattr(self,k)().load(v)
    
    def save(self):
        store_dict = OrderedDict()
        for k in self.mutators:
            store_dict[k] = getattr(self,k)()
        for k in self.accessors:
            store_dict[k] = getattr(self,k)().save()
        return store_dict
                        
class CPD:
    def create_mutator(self,key):
        def fn(value = None,autosave=True):
            data_k = "__node_data_"+key
            if value != None and getattr(self,data_k) != value:
                setattr(self,data_k,value)
                if autosave:
                    self.node.network.save()
                pub.sendMessage("node_changed", {"node":self.node,"key":self.key+"."+key})
            return getattr(self,data_k)
        self.mutators.append(key)
        return fn    
    
    def __init__(self,node,schema,key):
        self.node = node
        self.key = key
        self.mutators = []
        self.accessors = []
        for k,v in schema.items():
            data_k = "__node_data_"+k
            setattr(self,data_k,v)
            setattr(self,k,self.create_mutator(k))
    
    def load(self,json):
        for k,v in json.items():
            if k in self.mutators:
                getattr(self,k)(v,False)
            elif k in self.accessors:
                getattr(self,k)().load(v)
    
    def save(self):
        store_dict = OrderedDict()
        for k in self.mutators:
            store_dict[k] = getattr(self,k)()
        for k in self.accessors:
            store_dict[k] = getattr(self,k)().save()
        return store_dict
    
    def __str__(self):
        if self.expression()!="":
            return self.expression()
        else:
            return self.distribution()
        
class ModelIDE:

    def hello(self, widget, data=None):
        print self.network.name

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self,network):
        self.network = network
        self.in_select_node = False
        self.node = None
        
        self.gladefile = "ide.glade"
        builder = gtk.Builder()
        builder.add_from_file(self.gladefile)
        self.window = builder.get_object("ide")
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        self.graph = xdot.DotWidget()
        builder.get_object("hpane_nav").pack2(self.graph)
        self.graph.connect('clicked', self.on_graph_clicked)
        
        self.node_list_view = builder.get_object("node_list_view")
        self.node_param_holder = builder.get_object("node_param_holder")
        
        self.node_list_store = gtk.ListStore(str)
        self.node_list_view.set_model(self.node_list_store)
        
        tvcolumn = gtk.TreeViewColumn('id')
        self.node_list_view.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tvcolumn.set_sort_column_id(0)
        
        self.node_list_view.connect("cursor-changed",self.on_list_clicked)
        
        self.update_node_list()
        self.update_graph()
        self.graph.zoom_to_fit()
        if len(self.network.nodes)>0:
            self.select_node(self.network.nodes[0].id())
        
        self.btn_add = builder.get_object("btn_add")
        self.btn_remove = builder.get_object("btn_remove")
        
        self.btn_add.connect("clicked",self.on_btn_add_clicked)
        self.btn_remove.connect("clicked",self.on_btn_remove_clicked)
        
        pub.subscribe(self.on_node_changed ,"node_changed")
        pub.subscribe(self.on_node_added ,"node_added")
        pub.subscribe(self.on_node_removed ,"node_removed")
        
        self.window.show_all()
        
    def on_node_changed(self,msg):
        self.update_graph()
        self.update_node_list()
    
    def on_node_added(self,msg):
        self.update_graph()
        self.update_node_list()
        new_node = msg.data["node"]
        self.select_node(new_node.id())
        
    def on_node_removed(self,msg):
        self.update_graph()
        self.update_node_list()
        self.select_node(None)
        
    def main(self):
        gtk.main()
    
    def on_btn_add_clicked(self,button):
        self.network.add_node()
        
    def on_btn_remove_clicked(self,button):
        self.network.remove_node(self.node)
        
    def on_graph_clicked(self, widget, url, event):
        self.select_node(url)
        return True
        
    def on_list_clicked(self, widget):
        (m,i) = self.node_list_view.get_selection().get_selected()
        self.select_node(m.get_value(i,0))
        return True
    
    def update_node_list(self):
        self.node_list_store.clear()
        for node in self.network.nodes:
            self.node_list_store.append((node.id(),))
        if not self.node is None:
            self.in_select_node = True
            self.node_list_view.set_cursor(self.get_node_path(self.node.id()))
            self.in_select_node = False
            
    def update_graph(self):
        self.graph.set_dotcode(self.network.generate_dot(), filename='<stdin>')
        #self.graph.zoom_to_fit()
    
    def select_node(self,id):
        if not self.in_select_node:
            self.in_select_node = True
            self.node = self.network.get_node(id)
            try:
                self.node_param_holder.get_child().destroy()
            except:
                pass
                
            if self.node != None:
                self.node_list_view.set_cursor(self.get_node_path(id))
                nodepane = NodeIDEPane(self.node)
                self.node_param_holder.add_with_viewport(nodepane.widget)
            self.in_select_node = False
                
    def get_node_path(self,id):
        ctr = 0
        for node in self.network.nodes:
            if node.id() == id:
                return (ctr,)
            ctr+=1
        return (-1,)
    
class NodeIDEPane:
    def __init__(self,node):
        self.node = node
        num_entries = len(node.mutators)+len(node.accessors)
        table = gtk.Table(num_entries,2)
        ctr = 0
        
        def add_entry(obj,k):
            label = gtk.Label("")
            label.set_markup("<b>"+k.replace("_"," ").capitalize()+"</b>")
            table.attach(label,0,1,ctr,ctr+1)
            entry =  gtk.Entry()
            entry.set_text(self.get_text(obj,k))
            table.attach(entry,1,2,ctr,ctr+1)
            entry.connect("focus-out-event",self.create_focus_callback(obj,k))
            entry.connect("activate",self.create_activate_callback(obj,k))
            
        for k in node.mutators:
            add_entry(self.node,k)
            ctr+=1
            
        for k in node.accessors:
            label = gtk.Label("")
            label.set_markup("<b>"+k.replace("_"," ").capitalize()+"</b>")
            event_box = gtk.EventBox()
            event_box.add(label)
            style = event_box.get_style().copy()
            style.bg[gtk.STATE_NORMAL] = event_box.get_colormap().alloc('darkgrey')
            event_box.set_style(style)
            table.attach(event_box,0,2,ctr,ctr+1)
            child = getattr(node,k)()
            ctr+=1
            for child_k in child.mutators:
                add_entry(child,child_k)
                ctr+=1
            
        self.widget= table
        self.widget.show_all()
    
    def create_focus_callback(self,obj,k):
        def fn(entry,event):
            self.set_text(obj,k,entry.get_text())
        return fn
    
    def create_activate_callback(self,obj,k):
        def fn(entry):
            self.set_text(obj,k,entry.get_text())
        return fn
        
    def get_text(self,obj,k):
        item = getattr(obj,k)()
        if isinstance(item, basestring):
            return str(item)
        try:
            return ", ".join(str(x) for x in item)
        except TypeError:
            return str(item)
    
    def convert_type(self,string):
        string = string.strip()
        try:
            return int(string)
        except:
            pass
            
        try:
            return float(string)
        except:
            pass
        
        try:
            if string.lower() == "true":
                return True
            elif string.lower() == "false":
                return False
        except:
            pass
        
        return string
        
    def set_text(self,obj,k,value):
        item = getattr(obj,k)()
        if isinstance(item,list):
            getattr(obj,k)(filter(lambda x:x!="",map(self.convert_type,value.split(","))))
        else:
            getattr(obj,k)(self.convert_type(value))
    
def start_ide(model_filename):
    network = Network(model_filename)
    ModelIDE(network).main()
    
if __name__ == "__main__":
    start_ide("model.json")
