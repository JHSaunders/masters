#Copyright 2010 James Saunders
#
#This file is part of Web BPDA.
#
#Web BPDA is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Web BPDA.  If not, see <http://www.gnu.org/licenses/>.
from cgi import escape

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
            cpt = self.node.CPT().get_cpt_values()            
            for i in range(len(cpt)):
                defaults["cpt_%s"%(i,)] = cpt[i][1]            
            args=(defaults,)
        
        del kwargs["node"]
        super(CPTForm,self).__init__(*args,**kwargs)
                
        cpt = self.node.CPT().get_cpt_values()            
        for i in range(len(cpt)):
            self.fields["cpt_%s"%(i,)] = FloatField()
                
    def save_values(self):
        cpt = self.node.CPT().get_cpt_values()
        values = []
        for vi in range(len(cpt)):
            values.append(self.cleaned_data["cpt_%s"%(vi,)])
        self.node.CPT().set_cpt_values(values)        
                        
    def __unicode__(self):    
        
        cpt = self.node.CPT().get_cpt_values()
        if len(cpt)==0:
            return""
        parent_nodes = self.node.parent_nodes()
        num_val_cols = self.node.states.count()        
        num_index_cols = len(cpt[0][0])-1
        num_rows = len(cpt)/num_val_cols

        buf = []
        vi = 0
        buf.append("<tr>")        
        for p in parent_nodes:
            buf.append('<th>%s</th>'%escape(str(p)))
        for s in self.node.states.all():
            buf.append('<th>%s</th>'%escape(str(s)))                        
        buf.append("</tr>")

        for ri in range(num_rows):
            if ri % 2 == 0:
                buf.append("<tr>")
            else:
                buf.append('<tr class="alt">')

            for ci in range(num_index_cols):
                buf.append('<th>%s</th>'%(parent_nodes[ci].states.all()[cpt[vi][0][ci]]))
                
            for ci in range(num_val_cols):
                buf.append('<td class="cpt_cell">%s%s</td>'%(self["cpt_%s"%(vi,)].errors,self["cpt_%s"%(vi,)]))
                vi+=1
                
            buf.append("</tr>")
                
        return "".join(buf)

class ReasoningJustificationForm(Form):
    action = CharField(required=False)
    reason = Field(required=False,widget=Textarea)

class UploadForm(Form):
    file = FileField(required=True)
    
class CopyNetworkListForm(Form):
    copy_network=ModelChoiceField(queryset=Network.objects.all(),required=False)
