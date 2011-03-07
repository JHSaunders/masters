import gtk
import xdot
import dbn_processing

import matplotlib
matplotlib.use('GTK')
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar

class ResultViewer(gtk.Window):
    def __init__(self,model,params,results):
        super(ResultViewer, self).__init__()
        
        self.model = model
        self.results = results
        
        self.connect("destroy", gtk.main_quit)
        self.set_size_request(800, 600)
        self.set_title(model["properties"]["name"])
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.vbox = gtk.VBox()
        
        self.time = gtk.SpinButton()
        self.time.set_range(0,len(results)-1)
        self.time.set_numeric(True)
        self.time.set_increments(1,1)
        self.time.connect('value-changed', self.on_time_changed)
        self.vbox.pack_start(self.time,False)
        
        self.hbox = gtk.HBox()
        self.add(self.hbox)
        self.graph = xdot.DotWidget()
        
        self.hbox.pack_start(self.graph)
        self.set_focus(self.graph)
        dotcode = dbn_processing.generate_dot(model)
        
        self.graph.set_dotcode(dotcode, filename='<stdin>')
        self.graph.zoom_to_fit()
        self.graph.connect('clicked', self.on_url_clicked)

        self.current_node = None
        
        self.hbox.pack_start(self.vbox)
        
        self.init_chart()
        
        self.show_all()
    
    def init_chart(self):
        self.figure = Figure(figsize=(6,4), dpi=72)
        self.axis = self.figure.add_subplot(111)
        self.axis.set_xlabel('Yepper')
        self.axis.set_ylabel('Flabber')   
        self.axis.set_title('An Empty Graph')
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
            dbn_processing.setup_node_states(self.model["nodes"])
            for n in self.model["nodes"]:
                if n["id"] == self.current_node:
                    node = n
                    break
            
            left = map(lambda x: x[0],n["states"])
            width = map(lambda x: x[1] - x[0],n["states"])

            self.axis.set_xlabel('')
            self.axis.set_ylabel('')

            self.axis.set_title("{1} ({0})".format(self.current_node,n["label"]))            
            values = self.results[int(self.time.get_value())][self.current_node]
            self.axis.bar(left, values, width, color='b')  
            self.axis.set_xlim(left[0],left[-1]+width[-1])
            self.axis.set_ylim(0,1)
            self.canvas.draw()

                

            
def run_viewer(model,params,results):
    ResultViewer(model,params,results)
    gtk.main()
