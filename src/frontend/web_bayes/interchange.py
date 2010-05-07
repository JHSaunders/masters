import xml.dom.minidom

from backends.bke_openbayes import ExportToXBN

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
    return ExportToXBN(network)
