import csv
import sys
import urllib2
import json
import time
import xmltodict


def get_arxiv_url(title):
    
    title = title[:-1]
    print title
    ti = urllib2.quote('"' + title + '"')
    url = "http://export.arxiv.org/api/query?search_query=ti:" + ti + "&start=0&max_results=1"
    
    arxiv_xml = urllib2.urlopen(url).read()
    
    arxiv = xmltodict.parse(arxiv_xml)    
    arxiv = arxiv["feed"]
    
    nb_results = int(arxiv["opensearch:totalResults"]["#text"])
    
    if nb_results == 1:
       arxiv = arxiv["entry"]
       arxiv_title = arxiv["title"]
       print arxiv_title
       
       if arxiv_title.lower() == title.lower():
          arxiv_url = arxiv["id"] 
          return arxiv_url
    return "null"       
       
       
input_file = sys.argv[1]
input = csv.reader(open(input_file, 'r'))

for line in input:
    print line[0]
    result = get_arxiv_url(line[0])
    print  result
    print "===="
    time.sleep(3)  

    
    
    