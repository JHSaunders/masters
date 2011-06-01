#!/usr/bin/env python
import os

import pygtk
pygtk.require('2.0')
import gtk

from network import *
from pubsub import Publisher as pub
import xdot

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
        
        self.gladefile = os.path.dirname(__file__)+"/ide.glade"
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
        
        if len(self.network.nodes)>0:
            self.graph.zoom_to_fit()
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
                nodepane = SchemaLoadedObjectEditor(self.node)
                self.node_param_holder.add_with_viewport(nodepane.widget)
            self.in_select_node = False
                
    def get_node_path(self,id):
        ctr = 0
        for node in self.network.nodes:
            if node.id() == id:
                return (ctr,)
            ctr+=1
        return (-1,)
    
class SchemaLoadedObjectEditor(object):
    def __init__(self,obj):
        table = gtk.Table(1,3)
        ctr = 0
        
        def add_entry(obj,k):
            label = gtk.Label("")
            label.set_markup("<b>"+k.replace("_"," ").capitalize()+"</b>")
            label.set_alignment(0,0.5)
            table.attach(label,0,2,ctr,ctr+1)
            entry =  gtk.Entry()
            entry.set_text(self.get_text(obj,k))
            table.attach(entry,2,3,ctr,ctr+1,yoptions=gtk.SHRINK)
            entry.connect("focus-out-event",self.create_focus_callback(obj,k))
            entry.connect("activate",self.create_activate_callback(obj,k))
            
        for k in obj.mutators:            
            add_entry(obj,k)
            ctr+=1
            
        for k in obj.children:
            label = gtk.Label("")
            label.set_markup("<b>"+k.replace("_"," ").capitalize()+"</b>")
            event_box = gtk.EventBox()
            event_box.add(label)
            style = event_box.get_style().copy()
            style.bg[gtk.STATE_NORMAL] = event_box.get_colormap().alloc('darkgrey')
            event_box.set_style(style)            
            table.attach(event_box,0,3,ctr,ctr+1)
            ctr+=1        
            child = getattr(obj,k)()            
            child_widget = SchemaLoadedObjectEditor(child).widget
            table.attach(child_widget,1,3,ctr,ctr+1)
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
