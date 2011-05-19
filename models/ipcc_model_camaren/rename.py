import csv

rdr =  csv.reader(open("nodes.csv"))

rows = list(rdr)

rows.sort(key=lambda x: -len(x[0]))

dot = open("s0.dot")

fulltext = "".join(list(dot))

for row in rows:
    fulltext =fulltext.replace(row[0],row[1])

for row in rows:
    fulltext =fulltext.replace(row[0],row[1])
    
for row in rows:
    fulltext =fulltext.replace(row[0],row[1])

print fulltext
