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

FIRST_YEAR = 2013
LAST_YEAR = 2018

#################################################

# black-list are papers that must not be counted (e.g., in invalid tracks)
# white-list are papers that must be counted (e.g. with missing page numbers)
black_list = {}
white_list = {}

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
  if len(page) == 2:
     p1 = page[0]
     p2 = page[1]
     return int(p2) - int(p1) + 1
  elif (len(page) == 4):
     p1 = page[1]
     p2 = page[3]
     return int(p2) - int(p1) + 1
  else:
     return 0

#################################################

def output_venues():
  global out, conflist, journallist;

  confs = []
  journals = []
  f1 = open(area_prefix + '-out-confs.csv','w')
  f2 = open(area_prefix + '-out-journals.csv','w')

  for p in out.items():
    if (p[1][7] == "C"):
       confs.append(p[1][1])
    else:
       journals.append(p[1][1])
       
  result1 = sorted([(c, confs.count(c)) for c in conflist], key=lambda x: x[1], reverse=True)
  result2 = sorted([(c, journals.count(c)) for c in journallist], key=lambda x: x[1], reverse=True)

  for c in result1:
      f1.write(c[0]);
      f1.write(',')
      f1.write(str(c[1]));
      f1.write('\n')
  f1.close()
  
  for j in result2:
      f2.write(j[0]);
      f2.write(',')
      f2.write(str(j[1]));
      f2.write('\n')
  f2.close()

def output_papers():
  global out;

  # original code
  # sorted_papers = sorted(out.items(), key=lambda x: (x[1][1],x[1][0],x[1][2]))
  out2 = sorted(out.items(), key=lambda x: (x[1][1],x[1][2]))
  sorted_papers = sorted(out2, key=lambda x: x[1][0], reverse=True)
  
  f = open(area_prefix + '-out-papers.csv','w')
  for i in range(0, len(sorted_papers)):
      paper = sorted_papers[i][1]
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
      f.write(',')
      f.write(str(paper[7]))
      f.write('\n')
  f.close()

def output_scores():
  global score

  final_score = {}
  for dept in score:
      s = score[dept]
      if (s > 0):
         final_score[dept]= s

  sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
  sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)

  f2 = open(area_prefix + '-out-scores.csv','w')
  
  if (len(sorted_scores) >= 20):
     sorted_scores = filter(lambda dept: dept[1] >= 1.2, sorted_scores)
  
  for i in range(0, len(sorted_scores)):
      dept = sorted_scores[i][0]
      f2.write(str(dept))
      f2.write(',')
      s = sorted_scores[i][1]
      f2.write(str(s))
      f2.write('\n')
  f2.close()

def output_profs():
  global profs

  final_profs = {}
  for dept in profs:
      s = profs[dept]
      if (s > 0):
         final_profs[dept] = s

  sorted_profs_temp = sorted(final_profs.items(), key=lambda x: x[0])
  sorted_profs = sorted(sorted_profs_temp, key=lambda x: x[1], reverse=True)

  f3 = open(area_prefix + '-out-profs.csv','w')
  
  if (len(sorted_profs) >= 20):
     sorted_profs = filter(lambda dept: dept[1] >= 2, sorted_profs)
     
  for i in range(0, len(sorted_profs)):
      dept = sorted_profs[i][0]
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


def file_len(fname):
    with open(fname) as f:
       for i, l in enumerate(f):
           pass
    return i + 1

    
def flush_prof_papers(area_prefix, prof_name):
    num_lines = 0
    prof_name = prof_name.replace(" ", "-")
    file_name = "./profs/" + area_prefix + "-" + prof_name + '-papers.csv'
    if (os.path.exists(file_name)):
       num_lines = file_len(file_name)
       # print "Removing file " + file_name
       os.remove(file_name)   
    return num_lines


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
      f.write(',')
      f.write(str(paper[7]))
      f.write('\n')
  f.close()

def merge_output_prof_papers(profname):

    os.chdir("./profs")
    filenames = []
    profname = profname.replace(" ", "-")
    for file in glob.glob("*" + profname + "-papers.csv"):
        filenames.append(file)
        # print file
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
    if (weight == 1) or (weight == 4):
       return 1.0
    elif (weight == 2):
       return 0.66
    elif (weight == 3):
       return 0.33
    elif (weight == 5):
       return 0.4   
    else: 
       return 0.0   


def parse_dblp(_, dblp):
    global min_paper_size, department, found_paper, black_list

    if 'journal' in dblp:
        if (dblp['journal'] == "PACMPL") or (dblp['journal'] == "PACMHCI"):
           dblp_venue = dblp['number']
        else:
           dblp_venue = dblp['journal']
    elif 'booktitle' in dblp:
           dblp_venue = dblp['booktitle']
    else:
        return True

    year = int(dblp['year'])

    if ((year >= FIRST_YEAR) and (year <= LAST_YEAR)) and (dblp_venue in confdata):

        venue, weight = confdata[dblp_venue]
        url = dblp['url']

        if (year == 2018):
           print '\033[94m' + '*** 2018 *** '+ '\033[0m' + url

        pages = "null"
        
        if url in white_list:
            size = 10
        elif 'pages' in dblp:
            pages = dblp['pages']
            size = paperSize(pages)
        else:
            size = 0

        if (size >= min_paper_size):

            if url in black_list:
               return True

            found_paper = True;

            pid_papers.append(url)

            # this paper has been already processed
            if (url in out):
                paper = out[url]
                if (paper[3].find(department) == -1):
                   # but this author is from another department
                   paper2= (paper[0], paper[1], paper[2], paper[3] + "; " + department,
                            paper[4], paper[5], paper[6], paper[7])
                   out[url] = paper2
                   score[department] += inc_score(weight)
                return True

            title = dblp['title']
            if type(title) is collections.OrderedDict:
               title = title["#text"]
            title = title.replace("\"", "")  # remove quotes in titles

            # print '     ' + venue + ' ' + str(year) + ': '+ title
            print '      ' + venue + ' ' + str(year)
        
            doi = dblp['ee']
            if type(doi) is list:
               doi = doi[0]
            elif type(doi) is collections.OrderedDict:
               doi = doi["#text"]
            
            if (weight == 1) or (weight == 4):
               tier = "top"
            else:
               tier = "null"

            if (weight <= 3):
               vtype = "C"
            else:
               vtype = "J"

            authorList = dblp['author']
            authors = []
            for authorName in authorList:
                if type(authorName) is collections.OrderedDict:
                    authorName = authorName["#text"]
                authors.append(authorName)

            out[url] = (year, venue, '"' + title + '"', department, authors, doi, tier, vtype)
            score[department] += inc_score(weight)

    return True

# main program

area_prefix= sys.argv[1]
confs_file_name = area_prefix + "-confs.csv"

#for f in glob.glob("./profs/"+ area_prefix + "-*.csv"):
#    print "Removing file " + f
#    os.remove(f)

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
journallist = []
for conf_row in reader1:
  conf_dblp, conf_name, conf_weight = conf_row
  confdata[conf_dblp]= conf_name, int(conf_weight)
  if (int(conf_weight) <= 3):
     conflist.append(conf_name)
  else:
     journallist.append(conf_name)
conflist = list(set(conflist))  # removing duplicates
journallist = list(set(journallist))  # removing duplicates

out = {}
score = {}
profs = {}

init_black_white_lists()

reader2 = csv.reader(open(researchers_file_name, 'r'))
count = 1;
for researcher in reader2:

    prof_name = researcher[0]     # global variables
    department = researcher[1]
    pid = researcher[2]

    n0 = flush_prof_papers(area_prefix, prof_name)
    
    print str(count) + " >> " + prof_name + ", " + department + ", "+ str(n0)

    if not department in score:
       score[department]= 0.0
    if not department in profs:
       profs[department]= 0

    found_paper= False

    url= "http://dblp.org/pid/" + pid + ".xml"
    bibfile = urllib2.urlopen(url).read()

    pid_papers = []
    bibdata = xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)

    if found_paper:
       profs[department] += 1
       output_prof_papers(prof_name)
       merge_output_prof_papers(prof_name)
    elif (n0 > 0):
       print "*** has NO papers now **"
       merge_output_prof_papers(prof_name)
       
    count= count + 1;

output_papers()
output_scores()
output_profs()
output_venues()

generate_search_box_list()
