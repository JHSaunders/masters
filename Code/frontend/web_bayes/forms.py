from django.forms import *

from models import *

class EdgeForm(ModelForm):
    class Meta:
        model = Edge

class NodeForm(ModelForm):
    class Meta:
        model = Node
        
class CPTForm(Form):
    
    def __init__(self,*args,**kwargs): 
        
        self.node = kwargs["node"]
        if len(args) ==0:
            defaults = {}
            for tup in self.get_value_sets(): 
                for value in tup[1]:
                    defaults["%s"%(value.id,)] = value.value
            
            args=(defaults,)
        del kwargs["node"]
        super(CPTForm,self).__init__(*args,**kwargs)
        
        for tup in self.get_value_sets():
            for value in tup[1]:
                self.fields["%s"%(value.id,)] = FloatField()
        
    def get_value_sets(self):
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
           return []
        
        results = []
        
        while state_count<max_state_count:                
            parent_states = []
            for i in range(len(parent_nodes)):
                parent_states.append(parent_nodes[i].states.all()[current_states[i]])
            
            values = []
            for state in self.node.states.all():
                values.append(self.node.cpt_value(state,parent_states))
            
            results.append((parent_states,values))
                        
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
        
        return results
    
    def save_values(self):
        for tup in self.get_value_sets():
            for value in tup[1]:
                value.value = self.cleaned_data["%s"%value.id]
                value.save()
                
    def __unicode__(self):    
        value_set = self.get_value_sets()
                                    
        buf = []        
        buf.append("<tr>")
        for parent in self.node.parent_nodes():
            buf.append('<th>%s</th>'%(parent))
        buf.append("<td/>")        
        for state in self.node.states.all():
            buf.append("<th>%s</th>"%state)
        buf.append("</tr>")
        
        cycle = True;
      
        for tup in value_set:
            
            if cycle:
                buf.append("<tr>")
            else:
                buf.append('<tr class="alt">')
                
            for state in tup[0]:                
                buf.append('<td>%s</td>'%state)            
            buf.append('<td/>')            
            for value in tup[1]:
                buf.append('<td class="cpt_cell">%s%s</td>'% (self["%s"%(value.id,)].errors,self["%s"%(value.id,)]) )
            buf.append("</tr>")
            cycle = not cycle
                
        return "".join(buf)
