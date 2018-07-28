import csv
import sys
import urllib2
import json
import time

input_file = sys.argv[1]

input = csv.reader(open(input_file, 'r'))

mailto = "&mailto=mtvalente@gmail.com"

for line in input:
    doi_full = line[0]
    i = doi_full.find("10.")
    if i == -1:
       continue
    doi = doi_full[i:] 

    print doi
    
    # url = "https://api.crossref.org/works/" + doi + mailto
    
    # try:
    #  doi_entry = urllib2.urlopen(url).read()
    #  doi_json = json.loads(doi_entry)
    #  citations = doi_json["message"]["is-referenced-by-count"]
    #  print line[1] + ' ' + line[3] 
    #  print doi_full + '  ' + doi  + '   Cited by: ' + str(citations)
    # except:
    #  pass
    
    # time.sleep(10)  

    
    
    