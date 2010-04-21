from django.forms import *

from models import *

class EdgeForm(ModelForm):
    class Meta:
        model = Edge

class NodeForm(ModelForm):
    class Meta:
        model = Node
        
class CPTForm:
    
    def __init__(self,node):    
        self.node = node
        self.is_safe = True    
        
    def __unicode__(self):
        
        max_states = []
        state_count = 0
        max_state_count = 1
        current_states = []        
        parent_nodes = []
        for parent in self.node.parent_nodes():
            parent_nodes.append(parent)            
            max_states.append(parent.states.count())
            max_state_count*=parent.states.count()
            current_states.append(0)            

        if len(max_states)==0 or max_state_count == 0:
           return ""
                    
        buf = []        
        buf.append("<tr>")

        for parent in self.node.parent_nodes():
            buf.append('<th>%s</th>'%(parent))
        buf.append("<td/>");

        for state in self.node.states.all():
            buf.append("<th>%s</th>"%state)       

        buf.append("</tr>")
        
        cycle = True;
      
        while state_count<max_state_count:
            
            if cycle:
                buf.append("<tr>")
            else:
                buf.append('<tr class="alt">')
                
            parent_states = []
            for i in range(len(parent_nodes)):
                parent_states.append(parent_nodes[i].states.all()[current_states[i]])
                buf.append('<td>%s</td>'%parent_states[i])
            
            buf.append('<td/>')
            
            for state in self.node.states.all():
                value = self.node.cpt_value(state,parent_states);
                buf.append('<td>%s</td>'%value.id)
            
                
            buf.append("</tr>")
            
            cycle = not cycle
            state_count +=1
            running = True
            index = len(current_states) - 1
            while running:                
                current_states[index]+=1
                running = False
                if current_states[index]==max_states[index]:
                   current_states[index] = 0
                   running = True
                index-=1
                
                
        return "".join(buf)
