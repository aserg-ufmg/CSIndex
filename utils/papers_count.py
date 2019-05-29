# CSIndexbr: Exploring Brazilian Scientific Production in Computer Science

# @author: Marco Tulio Valente - ASERG/DCC/UFMG

# http://aserg.labsoft.dcc.ufmg.br

# How to run:
# on "utils" folder: python papers_count.py

import xmltodict
import re
import gzip
import time

FIRST_YEAR= 2013
LAST_YEAR= 2018
min_paper_size = 10

count = 0
papers = {}

def paperSize(dblp_pages, url):
  try:
    page= re.split(r"-|:", dblp_pages)
    if len(page) == 2:
       p1= page[0]
       p2= page[1]
       return int(p2) - int(p1) + 1
    elif len(page) == 4:
       p1= page[1]
       p2= page[3]
       return int(p2) - int(p1) + 1
    elif len(page) == 3:
       p1= page[1]
       p2= page[2]
       return int(p2) - int(p1) + 1
    else:
      print url
      return 0
  except:
     print url
     return 0


def parse_dblp(_, dblp):
    global count, papers, journals

    count += 1
    if count % 50000 == 0:
       print str(count)

    if 'year' in dblp:
       syear= dblp['year']
       year = int(syear)

       if ((year >= FIRST_YEAR) and (year <= LAST_YEAR)):
          if 'journal' in dblp:
              journal = dblp['journal']
              if journal in journals:
                 if 'pages' in dblp:
                    pages = dblp['pages']
                    if 'ee' in dblp:
                       size = paperSize(pages, dblp['ee'])
                    else:
                       size = paperSize(pages, "null")
                    if (size >= min_paper_size):
                       #print dblp['title']
                       papers[journal][year - FIRST_YEAR] += 1
    return True


# main program

start_time = time.time()

journals= {}
with open("journals.txt") as file:
   journals = file.read().splitlines()
for journal in journals:
    papers[journal] = [0, 0, 0, 0, 0, 0]

xmltodict.parse(gzip.GzipFile('dblp-fixed.xml.gz'), item_depth=2, item_callback=parse_dblp)

f = open("out.csv",'w')
for journal in journals:
    f.write(journal)
    f.write(',')
    f.write(str(papers[journal][0]))
    f.write(',')
    f.write(str(papers[journal][1]))
    f.write(',')
    f.write(str(papers[journal][2]))
    f.write(',')
    f.write(str(papers[journal][3]))
    f.write(',')
    f.write(str(papers[journal][4]))
    f.write(',')
    f.write(str(papers[journal][5]))
    f.write('\n')
f.close()

end_time = time.time()
elapsed_time = (end_time - start_time) / 60

print "Runtime (minutes): " + str(elapsed_time)
