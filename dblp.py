# CSIndexbr: Exploring Brazilian Scientific Production in Computer Science

# By Marco Tulio Valente - ASERG/DCC/UFMG
# http://aserg.labsoft.dcc.ufmg.br

# How to use (from data folder):
# python ../dblp.py

import csv
import sys
import requests
import time

start_time = time.time()
reader = csv.reader(open("all-researchers.csv", 'r'))
count = 1;
for researcher in reader:
    prof = researcher[0]
    department = researcher[1]
    pid = researcher[2]
    print str(count) + " >> " + prof + "," + department
    prof = prof.replace(" ", "-")
    file = '../cache/dblp/' + prof + '.xml'
    try:
       url = "http://dblp.org/pid/" + pid + ".xml"
       bibfile = requests.get(url).text
       with open(file, 'w') as f:
            f.write(bibfile)
    except requests.exceptions.RequestException as e:
       print e
       sys.exit(1)
    time.sleep(6)
    count = count + 1;
elapsed_time = (time.time() - start_time) / 60
elapsed_time = round(elapsed_time, 2)
print "Elapsed time (min): " + str(elapsed_time)
