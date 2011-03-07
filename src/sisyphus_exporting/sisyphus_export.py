import sys
import os
import MySQLdb
import xml.dom.minidom

dotctr = 0

def export(conn,scenario):

    cursor = conn.cursor (MySQLdb.cursors.DictCursor)
    cursor.execute ("SELECT scen.id,scen.path,ses.id,ses.session,w.workbook from scenarios scen, sessions ses, workbooks w  where scen.id=%s and w.id = scen.workbook and ses.id = scen.session"%(scenario,))

    info = cursor.fetchone()
    if info == None:
        return (None,None)
    print "Exporting %s , %s " % (info["session"],info["path"])
    session = int(info["ses.id"])
    workbook_name = info["workbook"]
    session_name = info["session"]
    scenario_name = info["path"]
    model_name = "%s %s %s"%(workbook_name,session_name,scenario_name)

    doc = xml.dom.minidom.Document()

    def appendNode(parent,tagname,text,attributes):
        node = doc.createElement(tagname.upper())

        
        if attributes!=None:
            for k,v in attributes.items():
                node.setAttribute(str(k).upper(),str(v))
        
        if text!=None: 
            node.appendChild(doc.createTextNode(str(text)))
        
        parent.appendChild(node)
        
        global dotctr        
        if dotctr % 100 == 0:
            sys.stdout.write(".")
        dotctr+=1
        return node
        
    root = appendNode(doc,"analysisnotebook",None,{"name":workbook_name,"root":model_name})    
    bnNode = appendNode(root,"bnmodel",None,{"name":model_name})
    #Static properties
    staticprops = appendNode(bnNode,"staticproperties",None,None)
    appendNode(staticprops,"version",1.0,None)
    appendNode(staticprops,"creator","Sisyphus",None)
    #Dynamic Properties
    dynprops = appendNode(bnNode,"dynamicproperties",None,None)    
    
    #Variables
    cursor.execute ("SELECT * from objects where type=0 and session=%s"%(session,))

    nodes = cursor.fetchall ()

    vars = appendNode(bnNode,"variables",None,None)
    for node in nodes:
        var = appendNode(vars,"var",None,{"name":node["name"],"type":"discrete","xpos":0,"ypos":0})
        appendNode(var,"fullname",node["name"],None)
        appendNode(var,"description",node["assumptions"],None)

        states_cursor = conn.cursor (MySQLdb.cursors.DictCursor)
    #    print ('SELECT * from cptpaths where scenario=%s and path like "%s%%"'%(scenario,node["path"]))
        states_cursor.execute ('SELECT * from cptpaths where scenario=%s and path like "%s%%"'%(scenario,node["path"]))   
        for state in states_cursor.fetchall():
            appendNode(var,"statename",state["pathState"],None)        
        
    #Structure
    cursor.execute ("SELECT DISTINCT s.name as source,d.name as destination from objects s,objects d,edges e where e.source=s.id and e.destination=d.id and e.session=%s"%(session,))
    edges = cursor.fetchall ()
    structure = appendNode(bnNode,"structure",None,None)
    for edge in edges:
        appendNode(structure,"arc",None,{"parent":edge["source"],"child":edge["destination"]})
    
    cursor.close ()
    return ((model_name).replace(' ','_')+".xml",doc.toprettyxml())

if __name__ == "__main__":
    username = sys.argv[1]
    passwd = sys.argv[2]
    conn = MySQLdb.connect (host = "localhost",
                           user = username,
                           passwd = passwd,
                           db = "csir")
                           
    cursor = conn.cursor (MySQLdb.cursors.DictCursor)
    cursor.execute ("SELECT id from scenarios")

    for row in cursor.fetchall():
        print row["id"]
        (filename,contents) = export(conn,row["id"])
        if filename != None:
            f = open(filename,'w')
            f.write(contents)
            f.close()
    conn.close ()
