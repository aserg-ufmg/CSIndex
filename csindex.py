# CSIndex Brasil: Exploring Brazilian Scientific Production in Computer Science

# @author: Marco Tulio Valente - ASERG/DCC/UFMG

# http://aserg.labsoft.dcc.ufmg.br

import xmltodict
import csv
import collections
import urllib2
import re
import sys
import operator
import glob
import os

## constants

FIRST_YEAR= 2013
LAST_YEAR= 2018

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

def paperSize(dblp_pages):
  page= re.split(r"-|:", dblp_pages)
  # print page
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

  # original code
  # sorted_papers = sorted(out.items(), key=lambda x: (x[1][1],x[1][0],x[1][2]))
  out2 = sorted(out.items(), key=lambda x: (x[1][1],x[1][2]))
  sorted_papers = sorted(out2, key=lambda x: x[1][0], reverse=True)
  
  f = open(area_prefix + '-out-papers.csv','w')
  for i in range(0, len(sorted_papers)):
    paper= sorted_papers[i][1]
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
    f.write(',')
    f.write(str(paper[5]))
    f.write(',')
    f.write(str(paper[6]))
    f.write('\n')
  f.close()

def output_scores():
  global score

  final_score = {}
  for dept in score:
    s= score[dept]
    if (s > 0):
       final_score[dept]= s

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
    s = sorted_profs[i][1]
    f3.write(str(s))
    f3.write('\n')
  f3.close()


def remove_prof_papers_file(area_prefix, prof_name):
    prof_name = prof_name.replace(" ", "-")
    file_name = "./profs/" + area_prefix + "-" + prof_name + '-papers.csv'
    if (os.path.exists(file_name)):
       print "Removing "+ file_name
       os.remove(file_name)

def output_prof_papers(prof_name):
  global out, pid_papers

  prof_name = prof_name.replace(" ", "-")
  f = open("./profs/" + area_prefix + "-" + prof_name + '-papers.csv','w')
  for url in pid_papers:
    paper= out[url]
    f.write(str(paper[0]))
    f.write(',')
    f.write(str(paper[1]))
    f.write(',')
    f.write(str(paper[2].encode('utf-8')))
    f.write(',')
    authors= paper[4]
    for author in authors[:-1]:
      f.write(str(author.encode('utf-8')))
      f.write('; ')
    f.write(str(authors[-1].encode('utf-8')))
    f.write(',')
    f.write(str(paper[5]))
    f.write(',')
    f.write(str(paper[6]))
    f.write('\n')
  f.close()

def merge_output_prof_papers(profname):

    os.chdir("./profs")
    filenames = []
    profname = profname.replace(" ", "-")
    for file in glob.glob("*" + profname + "-papers.csv"):
      filenames.append(file)
      print file
    outfile= open("./search/" + profname + ".csv", 'w')
    for fname in filenames:
        with open(fname) as infile:
           outfile.write(infile.read())
    os.chdir("..")

def generate_search_box_list():
    os.chdir("./profs/search")
    profs = []
    for file in glob.glob("*.csv"):
        file= file.replace(".csv", "")
        file= file.replace("-", " ")
        profs.append(file)
        print "prof: " + file
    profs.remove("empty")
    f = open("../all-authors.csv",'w')
    for p in profs:
      f.write(p)
      f.write('\n')
    f.close()

def output_pid_profs():
  global pid_profs

  f = open(area_prefix + "-" + 'out-profs-name.csv','w')
  for prof in pid_profs:
    f.write(prof)
    f.write('\n')
  f.close()


def inc_score(weight):
    if (weight == 1):
       return 1.0
    elif (weight == 2):
       return 0.66
    elif (weight == 3):
       return 0.33


def handle_article(_, article):
    global min_paper_size, department, found_paper, black_list

    if 'journal' in article:
        if (article['journal'] == "PACMPL") or (article['journal'] == "PACMHCI"):
           conf_name_dblp= article['number']
        else:
           return True
    elif 'booktitle' in article:
           conf_name_dblp= article['booktitle']
    else:
        return True

    year= article['year']

    if (int(year) >= FIRST_YEAR) and (int(year) <= LAST_YEAR) and (conf_name_dblp in confdata):

        conf_name, conf_weight = confdata[conf_name_dblp]
        url = article['url']

        if (int(year) == 2018):
           print '*** 2018 *** ' + url

        dblp_pages = "null"
        
        if url in white_list:
            size = 10
        elif 'pages' in article:
            dblp_pages = article ['pages']
            size = paperSize(dblp_pages)
        else:
            size = 0

        #if 'pages' in article:
        #    dblp_pages = article ['pages']
        #    size = paperSize(dblp_pages)
        #elif url in white_list:
        #    size = 10
        #else:
        #    size = 0

        if (size >= min_paper_size):

            if url in black_list:
               return True

            found_paper = True;

            pid_papers.append(url)

            # this paper has been already processed
            if (url in out):
                paper= out[url]
                if (paper[3].find(department) == -1):
                   # but this author is from another department
                   paper2= (paper[0], paper[1], paper[2], paper[3] + "; " + department,
                            paper[4], paper[5], paper[6])
                   out[url] = paper2
                   score[department] += inc_score(conf_weight)
                return True

            title = article['title']
            if type(title) is collections.OrderedDict:
               title = title["#text"]
            title = title.replace("\"", "")  # remove quotes in titles

            print conf_name + ' ' + year + ': '+ title
        
            if type(article['ee']) is list:
               dblp_doi = article['ee'][0]
            else:
               dblp_doi = article['ee']

            if (conf_weight == 1):
               conf_tag = "top"
            else:
               conf_tag = "null"

            authorList = article['author']
            authors = []
            for authorName in authorList:
                if (type(authorName) is collections.OrderedDict):
                    authorName = authorName["#text"]
                authors.append(authorName)

            out[url] = (year, conf_name, '"' + title + '"', department, authors, dblp_doi, conf_tag)
            score[department] += inc_score(conf_weight)

    return True


################################################################

# main program

area_prefix= sys.argv[1]
confs_file_name = area_prefix + "-confs.csv"

for f in glob.glob("./profs/"+ area_prefix + "-*.csv"):
    print "Removing file " + f
    os.remove(f)

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
  confdata[conf_dblp]= conf_name, int(conf_weight)
  conflist.append(conf_name)
conflist = list(set(conflist))  # removing duplicates

out = {}
score = {}
profs = {}

init_black_white_lists()

reader2 = csv.reader(open(researchers_file_name, 'r'))
count = 1;
for researcher in reader2:

    prof_name= researcher[0]     # global variables
    department= researcher[1]
    pid= researcher[2]

    print str(count) + " >> " + prof_name

    # remove_prof_papers_file(area_prefix, prof_name)

    if not department in score:
       score[department]= 0.0
    if not department in profs:
       profs[department]= 0

    found_paper= False

    url= "http://dblp.org/pid/" + pid + ".xml"
    bibfile = urllib2.urlopen(url).read()

    pid_papers = []
    bibdata = xmltodict.parse(bibfile, item_depth=3, item_callback=handle_article)

    if found_paper:
       profs[department] += 1
       output_prof_papers(prof_name)
       merge_output_prof_papers(prof_name)

    count= count + 1;

output_papers()
output_scores()
output_profs()
output_conferences()

generate_search_box_list()
