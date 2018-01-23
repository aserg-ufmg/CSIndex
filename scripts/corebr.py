import xmltodict
import csv
import collections
import urllib2
import re
import sys
import operator

min_paper_size= int(sys.argv[3])
   
reader1 = csv.reader(open(sys.argv[1], 'r'))
confdata = {}
for conf_row in reader1:
  conf_dblp, conf_name, conf_weight = conf_row
  confdata[conf_dblp]= conf_name, conf_weight
  
f = open('out.csv','w')

################################################################

## The following two functions are reused from CSRankings code

pageCounterNormal = re.compile('(\d+)-(\d+)')
pageCounterColon = re.compile('[0-9]+:([1-9][0-9]*)-[0-9]+:([1-9][0-9]*)')


def startpage(pageStr):
    global pageCounterNormal
    global pageCounterColon
    if pageStr is None:
        return 0
    pageCounterMatcher1 = pageCounterNormal.match(pageStr)
    pageCounterMatcher2 = pageCounterColon.match(pageStr)
    start = 0

    if not pageCounterMatcher1 is None:
        start = int(pageCounterMatcher1.group(1))
    else:
        if not pageCounterMatcher2 is None:
            start = int(pageCounterMatcher2.group(1))
    return start

def pagecount(pageStr):
    if pageStr is None:
        return 0
    pageCounterMatcher1 = pageCounterNormal.match(pageStr)
    pageCounterMatcher2 = pageCounterColon.match(pageStr)
    start = 0
    end = 0
    count = 0

    if not pageCounterMatcher1 is None:
        start = int(pageCounterMatcher1.group(1))
        end = int(pageCounterMatcher1.group(2))
        count = end - start + 1
    else:
        if not pageCounterMatcher2 is None:
            start = int(pageCounterMatcher2.group(1))
            end = int(pageCounterMatcher2.group(2))
            count = end - start + 1
    return count

################################################################

processedArticles = {}

def inc_dept_score(weight, scores):
    s0= scores[0]
    s1= scores[1]
    s2= scores[2]
    if (weight == 1):
       s0= s0 + 1
    elif (weight == 2):
       s1= s1 + 1
    elif (weight == 3):
       s2= s2 + 1    
    return [s0,s1,s2]
        
def handle_article(_, article):
    global min_paper_size, departmet
    
    if 'journal' in article:
        if article['journal'] == "PACMPL":
           conf_name_dblp= article['number']
        else:
           return True   
    elif 'booktitle' in article:
           conf_name_dblp= article['booktitle']
    else:
        return True
         
    year= article['year']
              
    if (int(year) >= 2013) and (int(year) <= 2017) and (conf_name_dblp in confdata):
           
        conf_name, conf_weight = confdata[conf_name_dblp] 
  
        if 'pages' in article:
            pageCount = pagecount(article['pages'])
            startPage = startpage(article['pages'])
        else:
            pageCount = -1
            startPage = -1         
            
        if (pageCount >= min_paper_size):

            url= article['url']
            
            # this is a paper at ICSE Education Track, that must be discarded 
            if url == "db/conf/icse/icse2013.html#NetoCLGM13":
               return True
               
            if (url in out):
                paper= out[url]
                if (paper[3].find(department) == -1):
                   paper2= (paper[0], paper[1], paper[2], paper[3] + "+" + department, paper[4]) 
                   out[url] = paper2 
                   score[department] = inc_dept_score(int(conf_weight), score[department])
                return True
                     
            title = article['title']
            if type(title) is collections.OrderedDict:
                title = title["#text"]
            print(title)
               
            authorList = article['author']
            authors= []
            for authorName in authorList:
                if (type(authorName) is collections.OrderedDict):
                    authorName = authorName["#text"]
                authors.append(authorName) 
                
            out[url]= (year, conf_name, '"' + title + '"', department, authors)     
            score[department] = inc_dept_score(int(conf_weight), score[department])
                              
    return True    

out = {}
score = {}

reader2 = csv.reader(open(sys.argv[2], 'r'))
count = 1;
for researcher in reader2:
  print str(count) + " >> " + researcher[0]
  
  department= researcher[1]
  if not department in score:
     score[department]= [0, 0, 0]

  pid= researcher[2]
  url= "http://dblp.org/pid/" + pid + ".xml"
  bibfile = urllib2.urlopen(url).read()
  bibdata = xmltodict.parse(bibfile, item_depth=3, item_callback=handle_article)
  count= count + 1;
  
sorted_papers = sorted(out.items(), key=lambda x: (x[1][1],x[1][0],x[1][2]))

f = open('out.csv','w')
for i in range(0, len(sorted_papers)):
  paper= sorted_papers[i][1]
  f.write(str(i+1))
  f.write(',')
  f.write(str(paper[0]))
  f.write(',')
  f.write(str(paper[1]))
  f.write(',')
  f.write(str(paper[2].encode('utf-8')))
  f.write(',')
  f.write(str(paper[3]))
  f.write(',')
  for author in paper[4]:
    f.write(str(author.encode('utf-8')))
    f.write(',')
  f.write('\n')
f.close()

final_score = {}
for dept in score:
  s= score[dept]
  if (s[0] > 0) or (s[1] > 0) or (s[2] > 0):
     final_score[dept]= s[0] + (s[1] * 0.66) + (s[2] * 0.33)

sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)

     
f2 = open('score.csv','w')
for i in range(0, len(sorted_scores)):
  dept= sorted_scores[i][0]
  f2.write(str(dept))
  f2.write(',')
  s= sorted_scores[i][1]
  f2.write(str(s))
  f2.write('\n')

f2.close()