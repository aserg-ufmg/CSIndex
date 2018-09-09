import csv
import sys
import requests
import time

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
    time.sleep(3)
    count = count + 1;
