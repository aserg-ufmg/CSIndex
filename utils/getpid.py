import xmltodict
import csv
import sys

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
def handle_author(_, author):
    
    global pid
    if 'hits' in author:
       x1 = author['hits']
       x2 = x1['hit']
       if type(x2) is list:
          x3= x2[0]
          x3= x3['info']
          x4 = x3['url'] + " alias"
       else:
          x3 = x2['info']
          x4 = x3['url']
       pid = x4.replace("http://dblp.org/pid/","")
       print (pid)
       return True
    pid= "null"   
    return False


f2 = open('out-researchers.csv','w')    

reader2 = csv.reader(open(sys.argv[1], 'r'))
count = 1;
pid = "null"
for researcher in reader2:
  print (str(count) + " >> " + researcher[0])
  
  query = urllib2.quote(researcher[0])
  url_dblp = 'http://dblp.org/search/author/api?q=%s' % (query)
  bibfile = urllib2.urlopen(url_dblp).read()
   
  xmltodict.parse(bibfile, item_depth=1, item_callback=handle_author)

  f2.write(researcher[0])
  f2.write(',')
  f2.write(researcher[1])
  f2.write(',')
  f2.write(pid) 
  f2.write('\n')
   
  count= count + 1;
  print ("####################################")
  
f2.close  
    
  
