#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys
import re

try:
    conn = mdb.connect('localhost', 'root', 
        'hardtofind', 'ipcc_final');

    cursor = conn.cursor(mdb.cursors.DictCursor)
    cursor.execute("SELECT * from objects WHERE type=0")    
    nodes = cursor.fetchall()    
    cursor.close()

    
    print """digraph {"""
    
    #Nodes
    for row in nodes:
        description = (row["constraints"],row["assumptions"],row["sources"])
        id = row["id"]
        name = row["name"].replace("\r\n"," ").replace("\n"," ").replace("\r"," ").strip()
        
        #Find States
        cursor = conn.cursor(mdb.cursors.DictCursor)
        cursor.execute('SELECT o.id,s.name FROM scenariostates as s, objects as o WHERE o.path = s.path and o.id = "{0}"'.format(id))
        states = cursor.fetchall()
        num_states = cursor.rowcount
        cursor.close() 
        
        if num_states >0:
            low = 1E10
            high = -1E10
            for state in states:
                state_str = state["name"]
                m = re.match("(-?\d+(\.\d+)?)-(-?\d+(\.\d+)?)",state_str)
                first = m.group(1)
                second = m.group(3)
                low = min(float(first),low)
                high = max(high,float(second))
            states_label =  "{0} : {1} : {2}".format(low,(high-low)/num_states,high)
            
        if row["output"]!="":
            if num_states>0:
                label = "{0}\\n{3}\\n{1}={2}".format(name,row["path"],row["output"],states_label)
            else:
                label = "{0}\\n{1}={2}".format(name,row["path"],row["output"])
        else:
            if num_states>0:
                label = "{0}\\n{3}\\n{1}".format(name,row["path"],row["output"],states_label)
            else:
                label = "{0}\\n{1}".format(name,row["path"],row["output"])
            
        
        print '{0}[label="{1}"]'.format(id,label,row["output"],description)
        
    
    #Edges
    cursor = conn.cursor(mdb.cursors.DictCursor)
    cursor.execute("SELECT edges.id, source,destination,srcs.path AS src_path ,dests.path AS dest_path from edges, objects AS srcs,objects AS dests WHERE edges.source = srcs.id AND edges.destination = dests.id") 
    edges = cursor.fetchall()
    cursor.close()
    for row in edges:
        print "{0}->{1}".format(row["source"].replace(" ","_"),row["destination"].replace(" ","_"))
    
    
    
    print """}"""

    conn.close()
    
except mdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
