# How to use (from data folder):
# python ../dblp.py
# python ../dblp.py -test (only test the cached files)

import csv
import sys
import requests
import time
import xmltodict
import os

def get_dblp_file(pid,prof):
    prof = prof.replace(" ", "-")
    file = '../cache/dblp/' + prof + '.xml'
    if os.path.exists(file):
       with open(file) as f:
          bibfile = f.read()
    else:
       try:
         url = "http://dblp.org/pid/" + pid + ".xml"
         bibfile = requests.get(url).text
         with open(file, 'w') as f:
            f.write(str(bibfile))
       except requests.exceptions.RequestException as e:
         print (e)
         sys.exit(1)
    return bibfile

def parse_dblp(_, dblp):
    if ('journal' in dblp) or ('booktitle' in dblp):
       return True
    return True

download = True
if len(sys.argv) == 2:
   if sys.argv[1] == "-test":
      download = False

if download:
   start_time = time.time()
   reader = csv.reader(open("all-researchers.csv", 'r'))
   count = 1;
   for researcher in reader:
       prof = researcher[0]
       department = researcher[1]
       pid = researcher[2]
       print (str(count) + " >> " + prof + "," + department)
       prof = prof.replace(" ", "-")
       file = '../cache/dblp/' + prof + '.xml'
       try:
         url = "http://dblp.org/pid/" + pid + ".xml"
         bibfile = requests.get(url).text
         with open(file, 'w') as f:
           f.write(bibfile)
       except requests.exceptions.RequestException as e:
         print (e)
         sys.exit(1)
       time.sleep(4)
       count = count + 1
   elapsed_time = (time.time() - start_time) / 60
   elapsed_time = round(elapsed_time, 2)
   print ("Elapsed time (min): " + str(elapsed_time))

print ("Testing files ....")
reader = csv.reader(open("all-researchers.csv", 'r'))
count = 1;
for researcher in reader:
    prof = researcher[0]
    department = researcher[1]
    pid = researcher[2]
    print (str(count) + " >> " + prof + "," + department)
    bibfile = get_dblp_file(pid,prof)
    xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)
    count = count + 1
