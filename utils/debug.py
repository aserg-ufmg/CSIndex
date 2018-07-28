import xmltodict
import urllib2
import re
import collections

FIRST_YEAR= 2017
LAST_YEAR= 2017

def paperSize(dblp_pages):
  page= re.split(r"-|:", dblp_pages) 
  print page
  if len(page) == 2:
     p1= page[0]
     p2= page[1]
     return int(p2) - int(p1) + 1
  elif (len(page) == 4):   
     p1= page[1]
     p2= page[3]
     return int(p2) - int(p1) + 1
  else:
     return 0
     
def handle_article(_, article):
       
    if ('booktitle' in article):
       year= article['year']
    else:
       return True
                 
    if (int(year) >= FIRST_YEAR) and (int(year) <= LAST_YEAR):
       print article['title']
       print article['booktitle']
       print year
       if ('pages' in article):
           dblp_pages = article ['pages']
           size = paperSize(dblp_pages)
           print dblp_pages
           print size
           
       authorList = article['author']
       
       #s = article['author']
       #if isinstance(s, basestring):
       #   print s
       
       authors = []
       for authorName in authorList:
           if (type(authorName) is collections.OrderedDict):
              authorName = authorName["#text"]
              authors.append(authorName)
              print authorName
           else:
              print authorName    
       return True
    
    
print '###########################################################'
    
url= "http://dblp.org/pid/" + "88/4732" + ".xml"


bibfile = urllib2.urlopen(url).read()
bibdata = xmltodict.parse(bibfile, item_depth=3, item_callback=handle_article)  
