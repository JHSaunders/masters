from django.forms import *

from models import *

class NetworkForm(ModelForm):
    class Meta:
        model= Network            
        widgets = {'users':CheckboxSelectMultiple}
        
class EdgeForm(ModelForm):
    class Meta:
        model = Edge
    
    def __init__(self,*args,**kwargs): 
        network = kwargs.get('network',None)
        instance = kwargs.get('instance',None)
        if network == None:
            network = instance.network
        else:
            del kwargs['network']
        
        super(EdgeForm,self).__init__(*args,**kwargs)
        
        self.fields['parent_node'].queryset = network.nodes.all()    
        self.fields['child_node'].queryset = network.nodes.all()

class NodeForm(ModelForm):
    class Meta:
        model = Node
        
    def __init__(self,*args,**kwargs): 
        
        super(NodeForm,self).__init__(*args,**kwargs)
        
        self.fields['cluster'].queryset = kwargs['instance'].network.clusters.all()    

class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
    nodes = ModelMultipleChoiceField(queryset=None,required=False,widget=CheckboxSelectMultiple())
    
    def __init__(self,*args,**kwargs):
        super(ClusterForm,self).__init__(*args,**kwargs)
        nodes_field = self.fields['nodes']
        nodes_field.queryset = kwargs['instance'].network.nodes.all()        
        nodes_field.initial = [c.id for c in kwargs['instance'].nodes.all()]
    
    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(ClusterForm, self).save(commit=False)

        for node in m.nodes.all():
            not_in_cluster = True
            for cluster_node in self.cleaned_data['nodes']:            
                if cluster_node == node:
                    not_in_cluster = False
                    
            if not_in_cluster:
                node.cluster = None
                node.save()
                 
        for node in self.cleaned_data['nodes']:
            node.cluster = m
            node.save()
        
        if commit:
            m.save()
        return m


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

class ReasoningJustificationForm(Form):
    action = CharField(required=False)
    reason = Field(required=False,widget=Textarea)

class UploadForm(Form):
    file = FileField(required=True)
