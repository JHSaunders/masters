import xml.dom.minidom

from backends.bke_openbayes import ExportToXBN
from models import *

def write_xml_bif(network):
    doc = xml.dom.minidom.Document()
    root = doc.createElementNS("http://unbbayes.sourceforge.net/xml/XMLBIF_0_6.xsd", "xbifns:XMLBIF")
    root.setAttribute("version","0.6")
    root.setAttribute("xmlns:xbifns","http://unbbayes.sourceforge.net/xml/XMLBIF_0_6.xsd")                    
    doc.appendChild(root)
    
    #header
    header = doc.createElement("xbifns:header")
    root.appendChild(header)   
     
    version = doc.createElement("xbifns:version")
    version.appendChild(doc.createTextNode(str(1.0)))
    header.appendChild(version)    
    
    name = doc.createElement("xbifns:name")
    name.appendChild(doc.createTextNode(str(network.name)))
    header.appendChild(name)    
    
    creator = doc.createElement("xbifns:creator")
    creator.appendChild(doc.createTextNode(str("webBPDA")))
    header.appendChild(creator)
    
    #network
    network_node = doc.createElement("xbifns:network")
    root.appendChild(network_node)
    
    return doc.toprettyxml()

def write_xbn(network):
    
    doc = xml.dom.minidom.Document()
    
    def appendNode(parent,tagname,text,attributes):
        node = doc.createElement(tagname.upper())
        
        if attributes!=None:
            for k,v in attributes.items():
                node.setAttribute(str(k).upper(),str(v))
        
        if text!=None: 
            node.appendChild(doc.createTextNode(str(text)))
        
        parent.appendChild(node)           
        return node
        
    root = appendNode(doc,"analysisnotebook",None,{"name":"webBPDA.%s"%(network.name,),"root":network.name})    
    bnNode = appendNode(root,"bnmodel",None,{"name":"%s"%(network.name,)})
    #Static properties
    staticprops = appendNode(bnNode,"staticproperties",None,None)
    appendNode(staticprops,"version",network.version,None)
    appendNode(staticprops,"creator","Web BPDA",None)
    #Dynamic Properties
    dynprops = appendNode(bnNode,"dynamicproperties",None,None)    
    #variables
    vars = appendNode(bnNode,"variables",None,None)
    for  node in network.nodes.all():
        var = appendNode(vars,"var",None,{"name":node.name,"type":"discrete","xpos":0,"ypos":0})
        appendNode(var,"fullname",node.name,None)
        appendNode(var,"description",node.description,None)
        
        for state in node.states.all():
            appendNode(var,"statename",state.name,None)        
    #structure
    structure = appendNode(bnNode,"structure",None,None)
    for edge in network.edges.all():
        appendNode(structure,"arc",None,{"parent":edge.parent_node.name,"child":edge.child_node.name})    
    
    #distributions
    dists = appendNode(bnNode,"distributions",None,None)
    for node in network.nodes.all():
        
        dist = appendNode(dists,"dist",None,{"type":"discrete"})
        appendNode(dist,"private",None,{"name":node.name})
        condset = appendNode(dist,"condset",None,None)
        for parent in node.parent_nodes():
            appendNode(condset,"condelem",None,{"name":parent.name})
        dpis = appendNode(dist,"dpis",None,None)
        
        if node.parent_edges.count()>0:
            valuesets = node.get_indexed_value_sets()[1]
            for valueset in valuesets:
                indexes = " ".join([str(st) for st in valueset[0]])
                values = " ".join([str(v.value) for v in valueset[1]])
                appendNode(dpis,"dpi",values,{"indexes":indexes})
        else:
            values = " ".join([str(s.probability) for s in node.states.all()])
            appendNode(dpis,"dpi",values,None) 
    
    return doc.toprettyxml()
    
def upload_xbn(file):
    doc = xml.dom.minidom.parse(file)
    network = Network(name=doc.getElementsByTagName("BNMODEL")[0].getAttribute("NAME"))
    network.save()                                                           
    nodemap = {}
    vars = doc.getElementsByTagName("VAR")
    for var in vars:
        node=Node(name=var.getAttribute("NAME"),network=network)
        
        try:
            node.description = var.getElementsByTagName("DESCRIPTION")[0].firstChild.data.strip()
        except:
            pass
            
        node.save()
        nodemap[node.name] = node
        for statename in var.getElementsByTagName("STATENAME"):
            state=State(name=statename.firstChild.data.strip(),node=node)
            state.save()
    
    arcs = doc.getElementsByTagName("ARC")
    for arc in arcs:
        parent_name = arc.getAttribute("PARENT")
        child_name = arc.getAttribute("CHILD")
        edge = Edge(network=network)
        edge.parent_node=nodemap[parent_name]
        edge.child_node=nodemap[child_name]
        edge.save()
    
    dists = doc.getElementsByTagName("DIST")
    for dist in dists:
        node = nodemap[dist.getElementsByTagName("PRIVATE")[0].getAttribute("NAME")]
        if node.parent_edges.count() >0:
            parents = [ nodemap[elem.getAttribute("NAME")] for elem in dist.getElementsByTagName("CONDELEM")]    
            print node, parents 
            for dpi in dist.getElementsByTagName("DPI"):
                indexes_string = dpi.getAttribute("INDEXES").strip()
                indexes = [int(i) for i in indexes_string.split(" ")]
                parent_states=[]
                print indexes
                for i in range(len(indexes)):
                    parent = parents[i]
                    parent_states.append(parent.states.all()[indexes[i]])
                cpts_strings = dpi.firstChild.data.strip().split(" ")
                child_states = node.states.all()
                
                for i in range(len(cpts_strings)):
                    cpt = node.cpt_value(child_states[i],parent_states)
                    cpt.value = float(cpts_strings[i])
                    cpt.save()
        else:
            dpi = dist.getElementsByTagName("DPI")[0]
            cpts_strings = dpi.firstChild.data.strip().split(" ")
            child_states = node.states.all()
            for i in range(len(cpts_strings)):
                state = child_states[i]
                state.probability = float(cpts_strings[i])
                state.save() 
    return network
    
