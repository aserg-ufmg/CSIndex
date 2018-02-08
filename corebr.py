import xmltodict
import csv
import collections
import urllib2
import re
import sys
import operator
import os.path

#################################################

# black-list are papers that must not be counted (e.g., in invalid tracks)
# white-list are papers that must be counted (e.g. with missing page numbers)
black_list= {}
white_list= {}

def init_black_white_lists():
   global black_list, white_list
   
   black_list_file= area_prefix + "-black-list.txt"
   if os.path.exists(black_list_file):
      with open(black_list_file) as blf:
        black_list = blf.read().splitlines()
   
   white_list_file= area_prefix + "-white-list.txt"
   if os.path.exists(white_list_file):
      with open(white_list_file) as wlf:
        white_list = wlf.read().splitlines()
   
#################################################

# The following two functions are reused from CSRankings code

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

#################################################

def output_conferences():
  global out, conflist;
  
  confs = []
  f = open(area_prefix + '-out-confs.csv','w')
  
  for p in out.items():
    confs.append(p[1][1]) 
    
  result = sorted([(c, confs.count(c)) for c in conflist], key=lambda x: x[1], reverse=True)
  
  for conf in result:
    f.write(conf[0]);
    f.write(',')
    f.write(str(conf[1]));
    f.write('\n')
  f.close()
    
def output_papers():
  global out;

  sorted_papers = sorted(out.items(), key=lambda x: (x[1][1],x[1][0],x[1][2]))
  f = open(area_prefix + '-out-papers.csv','w')
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
    authors= paper[4]
    for author in authors[:-1]:
      f.write(str(author.encode('utf-8')))
      f.write('; ')
    f.write(str(authors[-1].encode('utf-8')))  
    f.write('\n')
  f.close()

def output_scores():
  global score
  
  final_score = {}
  for dept in score:
    s= score[dept]
    if (s[0] > 0) or (s[1] > 0) or (s[2] > 0):
       final_score[dept]= s[0] + (s[1] * 0.66) + (s[2] * 0.33)

  sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
  sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)

  f2 = open(area_prefix + '-out-scores.csv','w')
  for i in range(0, len(sorted_scores)):
    dept= sorted_scores[i][0]
    f2.write(str(dept))
    f2.write(',')
    s= sorted_scores[i][1]
    f2.write(str(s))
    f2.write('\n')
  f2.close()

def output_profs():
  global profs
   
  final_profs = {}
  for dept in profs:
    s= profs[dept]
    if (s > 0):
       final_profs[dept]= s

  sorted_profs_temp = sorted(final_profs.items(), key=lambda x: x[0])
  sorted_profs = sorted(sorted_profs_temp, key=lambda x: x[1], reverse=True)

  f3 = open(area_prefix + '-out-profs.csv','w')
  for i in range(0, len(sorted_profs)):
    dept= sorted_profs[i][0]
    f3.write(str(dept))
    f3.write(',')
    s= sorted_profs[i][1]
    f3.write(str(s))
    f3.write('\n')
  f3.close()

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
    global min_paper_size, department, found_paper, black_list
    
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
        url= article['url']
               
        if 'pages' in article:
            pageCount = pagecount(article['pages'])
            startPage = startpage(article['pages'])
        elif url in white_list:
            pageCount = 10
            startPage = 1
        else:    
            pageCount = -1
            startPage = -1         
            
        if (pageCount >= min_paper_size):
                
            if url in black_list:
               return True
            
            found_paper= True;
               
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
            
            title = title.replace("\"", "")    
            
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

area_prefix= sys.argv[1]   

confs_file_name = area_prefix + "-confs.csv"

reader3 = csv.reader(open("research-areas-config.csv", 'r'))
for area_tuple in reader3:
  if (area_tuple[0] == area_prefix):
     researchers_file_name = area_tuple[1]  
     min_paper_size = int(area_tuple[2])
     break
     
print "Research Area: " + area_prefix
print "Researchers: " + researchers_file_name
print "Minimun paper size: " + str(min_paper_size)
   
reader1 = csv.reader(open(confs_file_name, 'r'))
confdata = {}
conflist = []
for conf_row in reader1:
  conf_dblp, conf_name, conf_weight = conf_row
  confdata[conf_dblp]= conf_name, conf_weight
  conflist.append(conf_name)
conflist = list(set(conflist))  
  
out = {}
score = {}
profs = {}
  
init_black_white_lists()
    
reader2 = csv.reader(open(researchers_file_name, 'r'))
count = 1;
for researcher in reader2:
  
  professor= researcher[0]
  department= researcher[1]
     
  print str(count) + " >> " + professor
  
  if not department in score:
     score[department]= [0, 0, 0]
  if not department in profs:
     profs[department]= 0
   
  pid= researcher[2]
  found_paper= False
  
  url= "http://dblp.org/pid/" + pid + ".xml"
  bibfile = urllib2.urlopen(url).read()
  bibdata = xmltodict.parse(bibfile, item_depth=3, item_callback=handle_article)
  
  if found_paper:
     profs[department]= profs[department] + 1
  
  count= count + 1;

output_papers()
output_scores()
output_profs()
output_conferences()