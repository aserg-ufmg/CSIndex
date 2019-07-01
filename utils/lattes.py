# How to use (from data folder):
# python ../dblp.py
# python ../dblp.py -test (only test the cached files)

import csv
import sys
import requests
import time
import xmltodict

def get_dblp_file(pid,prof):
    prof = prof.replace(" ", "-")
    file = '../cache/dblp/' + prof + '.xml'
    with open(file) as f:
       bibfile = f.read()
    return bibfile

lattes = ''

def parse_dblp(_, dblp):
    global lattes
    if ('url' in dblp):
       for url in dblp['url']:
           if url.find("lattes.cnpq.br") != -1:
              lattes = url
              return True
    return True

reader = csv.reader(open('all-researchers.csv', 'r'))
out = open('all-researchers-lattes.csv','w')
count = 1;
for researcher in reader:
    prof = researcher[0]
    department = researcher[1]
    pid = researcher[2]
    print str(count) + " >> " + prof + "," + department
    bibfile = get_dblp_file(pid,prof)
    lattes = ''
    xmltodict.parse(bibfile, item_depth=2, item_callback=parse_dblp)
    if lattes:
       lattes = lattes.replace('http://lattes.cnpq.br/','')
    out.write(prof)
    out.write(',')
    out.write(department)
    out.write(',')
    out.write(pid)
    out.write(',')
    out.write(lattes)
    out.write('\n')
    count = count + 1
out.close()
