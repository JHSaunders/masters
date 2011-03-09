import gtk
import gobject
import xdot
from dbn_processing import *

import matplotlib
matplotlib.use('GTK')
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar

def get_in_stream(name):
    if name =='-' or name==None:
        return sys.stdin
    else:
        return open(name,'r')

class ResultViewer(gtk.Window):
    def __init__(self,modelf,paramsf,resultsf,auto_update = 1):
        super(ResultViewer, self).__init__()
        self.model_file = modelf if modelf!=None else "model.json"
        self.param_file = paramsf
        self.results_file = resultsf
        self.connect("destroy", gtk.main_quit)
        self.set_size_request(800, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.vbox = gtk.VBox()
        
        self.time = gtk.SpinButton()
        self.time.set_numeric(True)
        self.time.set_increments(1,1)
        self.time.connect('value-changed', self.on_time_changed)
        self.vbox.pack_start(self.time,False)
        
        self.hbox = gtk.HPaned()
        self.add(self.hbox)
        self.graph = xdot.DotWidget()
        
        self.hbox.pack1(self.graph,True)
        self.set_focus(self.graph)
        
        self.graph.connect('clicked', self.on_url_clicked)

        self.current_node = None
        
        self.hbox.pack2(self.vbox,True)
        self.hbox.set_position(400)
        self.init_chart()
        if auto_update==1:
            import gobject
            gobject.timeout_add(500, self.update)
            self.update()
        else:
            self.reload()
            
        self.show_all()
    
    def reload(self):
        modelins = get_in_stream(self.model_file or "model.json")
        parameterins = get_in_stream(self.param_file or "prm.json")
        resultins = get_in_stream(self.results_file or "res.json")

        self.model = json.load(modelins)
        self.params = json.load(parameterins)
        self.results = json.load(resultins)

        modelins.close()
        parameterins.close()
        resultins.close()
        
        self.set_title(self.model["properties"]["name"])
        self.time.set_range(0,len(self.results)-1)
        
        dotcode = generate_dot(self.model)
        self.graph.set_dotcode(dotcode, filename='<stdin>')

        self.draw_chart()        
        dotcode = generate_dot(self.model)
        self.graph.set_dotcode(dotcode, filename='<stdin>')
        self.graph.zoom_to_fit()
    
    def update(self):
        import os
        import subprocess
        if not hasattr(self, "last_mtime"):
            self.last_mtime = None
        current_mtime = os.stat(self.model_file).st_mtime
        if current_mtime != self.last_mtime:
            self.last_mtime = current_mtime
            subprocess.call("make")
            self.reload()
        return True
    
    def init_chart(self):
        self.figure = Figure(figsize=(6,4), dpi=72)
        self.axis = self.figure.add_subplot(111)
        self.axis.grid(True)   
        self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea   
        self.canvas.show()
        self.vbox.pack_start(self.canvas, True, True)  
    
    def on_url_clicked(self, widget, url, event):
        self.current_node = url
        self.draw_chart()
        return True
    
    def on_time_changed(self,widget):
        self.draw_chart()
    
    def draw_chart(self):
        self.axis.clear()
        if not (self.current_node is None):
            setup_node_states(self.model["nodes"])
            for n in self.model["nodes"]:
                if n["id"] == self.current_node:
                    node = n
                    break
            
            left = map(lambda x: x[0],n["states"])
            width = map(lambda x: x[1] - x[0],n["states"])

            self.axis.set_xlabel('')
            self.axis.set_ylabel('Probability')
            self.axis.grid(True)
            self.axis.set_title("{1} ({0})".format(self.current_node,n["label"]))            
            values = self.results[int(self.time.get_value())][self.current_node]
            self.axis.bar(left, values, width, color='b')  
            self.axis.set_xlim(left[0],left[-1]+width[-1])
#            self.axis.set_ylim(0,1)
        self.canvas.draw()
            
def run_viewer(model,params,results,auto_update):
    ResultViewer(model,params,results,auto_update)
    gtk.main()
