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
            for tup in self.node.get_value_sets(): 
                for value in tup[1]:
                    defaults["%s"%(value.id,)] = value.value
            
            args=(defaults,)
        del kwargs["node"]
        super(CPTForm,self).__init__(*args,**kwargs)
        
        for tup in self.node.get_value_sets():
            for value in tup[1]:
                self.fields["%s"%(value.id,)] = FloatField()
    
    def save_values(self):
        for tup in self.node.get_value_sets():
            for value in tup[1]:
                if "%s"%value.id in self.cleaned_data: 
                    value.value = self.cleaned_data["%s"%value.id]
                    value.save()
                
    def __unicode__(self):    
        value_set = self.node.get_value_sets()
                                    
        buf = []        
        buf.append("<tr>")
        for parent in self.node.parent_nodes():
            buf.append('<th>%s</th>'%(parent))
        buf.append("<th/>")        
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
