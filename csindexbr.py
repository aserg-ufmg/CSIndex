import csv
import collections
import re
import sys
import operator
import glob
import os
import requests
import xmltodict
import json

from difflib import SequenceMatcher

FIRST_YEAR = 2014
LAST_YEAR = 2019

ALERT_ON = '\033[94m'
ALERT_OFF = '\033[0m'

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

manual_journals = {}
manual_classification = {}
mc_failed_file = open('manual-classification-failed.csv','a')
log = open('log.txt','a')

def init_manual_files():
    global manual_journals, manual_classification
    with open('manual-journals.txt') as mf:
         manual_journals = mf.read().splitlines()
    reader = csv.reader(open('manual-classification.csv', 'r'))
    for row in reader:
        m_area, m_year, m_venue, m_title, m_url = row
        manual_classification[m_url]= m_area

#################################################

mailto = "&mailto=mtvalente@gmail.com"
headers = {
    'User-Agent': 'csindexbr.org; mtvalente@gmail.com',
}

def open_citations_cache(area):
    global citations_cache
    citations_cache = {}
    fname = '../cache/citations/' + area + '-citations.csv'
    if os.path.exists(fname):
       reader = csv.reader(open(fname, 'r'))
       for line in reader:
           citations_cache[line[0]] = line[1]

def output_citations_cache(area):
    if citations_cache:
       f = open('../cache/citations/' + area + '-citations.csv','w')
       for doi in citations_cache:
           f.write(doi)
           f.write(',')
           f.write(str(citations_cache[doi]))
           f.write('\n')
       f.close()

def get_citations(doi):
    if doi in citations_cache:
       return citations_cache[doi]
    doi_full = doi
    i = doi_full.find("10.")
    if i == -1:
       log.write("DOI failed (for citations): " + doi + "\n")
       return -1
    doi = doi_full[i:]
    url = "https://api.crossref.org/works/" + doi
    try:
      r = requests.get(url, headers=headers)
      doi_json = json.loads(r.text)
      citations = doi_json["message"]["is-referenced-by-count"]
      citations_cache[doi_full] = citations
      return citations
    except:
      log.write("Crossref failed: " + doi + "\n")
      return -1

#################################################

def open_arxiv_cache(area):
    global arxiv_cache
    arxiv_cache = {}
    fname = '../cache/arxiv/' + area + '-arxiv-cache.csv'
    if os.path.exists(fname):
       reader = csv.reader(open(fname, 'r'))
       for line in reader:
           arxiv_cache[line[0]] = line[1]

def output_arxiv_cache(area):
    if arxiv_cache:
       f = open('../cache/arxiv/' + area + '-arxiv-cache.csv','w')
       for doi in arxiv_cache:
           f.write(doi)
           f.write(',')
           f.write(arxiv_cache[doi]);
           f.write('\n')
       f.close()

def get_arxiv_url(doi, title):
    if doi in arxiv_cache:
       return arxiv_cache[doi]
    try:
      title = title[:-1]
      ti = '"' + title + '"'
      url = "http://export.arxiv.org/api/query"
      payload = {'search_query': ti, 'start': 0, 'max_results': 1}
      arxiv_xml = requests.get(url, params=payload).text
      arxiv = xmltodict.parse(arxiv_xml)
      arxiv = arxiv["feed"]
      arxiv_url = "no_arxiv"
      nb_results = int(arxiv["opensearch:totalResults"]["#text"])
      if nb_results == 1:
         arxiv = arxiv["entry"]
         arxiv_title = arxiv["title"]
         t1 = arxiv_title.lower()
         t2 = title.lower()
         score = SequenceMatcher(None, t1, t2).ratio()
         if score >= 0.9:
            arxiv_url = arxiv["id"]
    except:
       log.write("arXiv failed: " + doi + "\n")
    arxiv_cache[doi] = arxiv_url
    return arxiv_url

#################################################

def asInt(i):
    try:
      return int(i)
    except:
      return 0

def paperSize(dblp_pages):
    page= re.split(r"-|:", dblp_pages)
    if len(page) == 2:
       p1 = asInt(page[0])
       p2 = asInt(page[1])
       return p2 - p1 + 1
    elif len(page) == 4:
       p1 = asInt(page[1])
       p2 = asInt(page[3])
       return int(p2) - int(p1) + 1
    elif len(page) == 3:
       p1 = asInt(page[1])
       p2 = asInt(page[2])
       return int(p2) - int(p1) + 1
    else:
       return 0

#################################################

def output_venues():
    global out, conflist, journallist;

    confs = []
    journals = []
    for p in out.items():
        if p[1][7] == "C":
           confs.append(p[1][1])
        else:
           journals.append(p[1][1])
    result1 = sorted([(c, confs.count(c)) for c in conflist], key=lambda x: x[1], reverse=True)
    result2 = sorted([(c, journals.count(c)) for c in journallist], key=lambda x: x[1], reverse=True)
    if len(result1) > 0:
       f1 = open(area_prefix + '-out-confs.csv','w')
       for c in result1:
           f1.write(c[0]);
           f1.write(',')
           f1.write(str(c[1]));
           f1.write('\n')
       f1.close()
    if len(result2) > 0:
       f2 = open(area_prefix + '-out-journals.csv','w')
       for j in result2:
           f2.write(j[0]);
           f2.write(',')
           f2.write(str(j[1]));
           f2.write('\n')
       f2.close()

def write_paper(f, is_prof_tab, paper):
    f.write(str(paper[0]))
    f.write(',')
    f.write(str(paper[1]))
    f.write(',')
    f.write(str(paper[2].encode('utf-8')))
    f.write(',')
    if is_prof_tab:
       f.write(str(paper[3]))  # department
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
    f.write(',')
    f.write(str(paper[8]))  # arxiv
    f.write(',')
    if paper[9] != -1:
       f.write(str(paper[9]))  # citations
    f.write('\n')

def output_papers():
    out2 = sorted(out.items(), key=lambda x: (x[1][1],x[1][2]))
    sorted_papers = sorted(out2, key=lambda x: x[1][0], reverse=True)
    f = open(area_prefix + '-out-papers.csv','w')
    for i in range(0, len(sorted_papers)):
        paper = sorted_papers[i][1]
        write_paper(f, True, paper)
    f.close()

def output_prof_papers(prof_name):
    prof_name = prof_name.replace(" ", "-")
    f = open("../cache/profs/" + area_prefix + "-" + prof_name + '-papers.csv','w')
    for url in pid_papers:
        paper= out[url]
        write_paper(f, False, paper)
    f.close()

def output_scores():
  global score

  final_score = {}
  for dept in score:
      s = score[dept]
      if s > 0:
         final_score[dept]= s

  sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
  sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)

  f2 = open(area_prefix + '-out-scores.csv','w')

  #if len(sorted_scores) >= 16:
     # sorted_scores = filter(lambda dept: dept[1] >= 1.5, sorted_scores)
    # sorted_scores = sorted_scores[:16]

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
      if s > 0:
         final_profs[dept] = s

  sorted_profs_temp = sorted(final_profs.items(), key=lambda x: x[0])
  sorted_profs = sorted(sorted_profs_temp, key=lambda x: x[1], reverse=True)

  f3 = open(area_prefix + '-out-profs.csv','w')

  if len(sorted_profs) >= 16:
     # sorted_profs = filter(lambda dept: dept[1] > 2, sorted_profs)
     sorted_profs = sorted_profs[:16]

  for i in range(0, len(sorted_profs)):
      dept = sorted_profs[i][0]
      f3.write(str(dept))
      f3.write(',')
      s = sorted_profs[i][1]
      f3.write(str(s))
      f3.write('\n')
  f3.close()

def output_profs_list():
    global profs_list

    profs_list = sorted(profs_list, key=lambda x: x[0])

    f3 = open(area_prefix + '-out-profs-list.csv','w')

    for i in range(0, len(profs_list)):
        f3.write(str(profs_list[i][0]))
        f3.write(',')
        f3.write(str(profs_list[i][1]))
        f3.write('\n')
    f3.close()


def remove_prof_papers_file(area_prefix, prof_name):
    prof_name = prof_name.replace(" ", "-")
    file_name = "../cache/profs/" + area_prefix + "-" + prof_name + '-papers.csv'
    if os.path.exists(file_name):
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
    file_name = "../cache/profs/" + area_prefix + "-" + prof_name + '-papers.csv'
    if os.path.exists(file_name):
       num_lines = file_len(file_name)
       os.remove(file_name)
    return num_lines

def merge_output_prof_papers(profname):
    os.chdir("../cache/profs")
    filenames = []
    profname = profname.replace(" ", "-")
    for file in glob.glob("*" + profname + "-papers.csv"):
        filenames.append(file)
    filenames.sort()
    outfile= open("../../data/profs/search/" + profname + ".csv", 'w')
    for fname in filenames:
        with open(fname) as infile:
             outfile.write(infile.read())
    os.chdir("../../data")

def generate_search_box_list():
    os.chdir("./profs/search")
    profs = []
    for file in glob.glob("*.csv"):
        file = file.replace(".csv", "")
        file = file.replace("-", " ")
        profs.append(file)
    profs.remove("empty")
    profs.sort()
    f = open("../all-authors.csv",'w')
    for p in profs:
        f.write(p)
        f.write('\n')
    f.close()

def inc_score(weight):
    if (weight == 1) or (weight == 4):
       return 1.0
    elif weight == 2:
       return 0.66
    elif (weight == 3) or (weight == 6) or (weight == 7):
       return 0.33
    elif weight == 5:
       return 0.4
    else:
       return 0.0

def getMinPaperSize(weight):
    if (weight == 6) or (weight == 7):  # magazine, short papers, other journals
       minimum_size = 6
    elif (weight == 4) or (weight == 5): # journals
       if area_prefix == "theory":
          minimum_size = 6
       else:
          minimum_size = 10
    else:
       minimum_size = MIN_PAPER_SIZE   # conferences
    return minimum_size

def getDOI(doi):
    if type(doi) is list:
       doi = doi[0]
    if type(doi) is collections.OrderedDict:
       doi = doi["#text"]
    return doi

def getVenueTier(weight):
    if (weight == 1) or (weight == 4):
       tier = "top"
    elif (weight == 2):
       tier = "near-top"
    else:
       tier = "null"
    return tier

def getVenueType(weight):
    if weight <= 3:
       venue_type = "C"
    else:
       venue_type = "J"
    return venue_type

def getAuthors(authorList):
    authors = []
    if type(authorList) is collections.OrderedDict: # single author paper
       authorList = authorList["#text"]
       authors.append(authorList)
    elif isinstance(authorList, basestring):  # single author paper
       if type(authorList) is collections.OrderedDict:
          authorList = authorList["#text"]
       authors.append(authorList)
    else:
       for authorName in authorList:
           if type(authorName) is collections.OrderedDict:
              authorName = authorName["#text"]
           authors.append(authorName)
    return authors

def getTitle(title):
    if type(title) is collections.OrderedDict:
       title = title["#text"]
    title = title.replace("\"", "")  # remove quotes in titles
    return title

def getPaperSize(url,dblp,doi):
    if url in white_list:
       size = 10
    elif 'pages' in dblp:
       pages = dblp['pages']
       size = paperSize(pages)
       if (size == 0):
          log.write('Missing pages: url: ' + url + ' doi: ' + doi + '\n')
    else:
       size = 0
       log.write('Missing pages: url: ' + url + ' doi: ' + doi + '\n')
    return size

def getDBLPVenue(dblp):
    if 'journal' in dblp:
        if (dblp['journal'] == "PACMPL") or (dblp['journal'] == "PACMHCI"):
           dblp_venue = dblp['number']
        else:
           dblp_venue = dblp['journal']
    elif 'booktitle' in dblp:
           dblp_venue = dblp['booktitle']
    else:
       print "Failed parsing DBLP: " + prof_name
       System.exit(1)
    return dblp_venue

def log_msg(venue,year,url):
    if (year == 2018):
       msg = str(year) + ' ' + venue + ' ' + url
       log.write(msg)
       log.write('\n')

def write_mc_failed(year,dblp_venue,title,url):
    global mc_failed_file, multi_area_journal
    mc_failed_file.write(",")
    mc_failed_file.write(str(year))
    mc_failed_file.write(",")
    mc_failed_file.write('"' + str(dblp_venue) + '"')
    mc_failed_file.write(",")
    mc_failed_file.write('"' + title.encode('utf-8') + '"')
    mc_failed_file.write(",")
    mc_failed_file.write(str(url))
    mc_failed_file.write("\n")
    multi_area_journal = True

def hasDept(dept_str, dept):
    dept_list = dept_str.split(";")
    for d in dept_list:
        d = d.replace(" ", "")
        if (d == dept):
           return True
    return False

def parse_dblp(_, dblp):
    global department, found_paper, black_list

    if ('journal' in dblp) or ('booktitle' in dblp):
       dblp_venue = getDBLPVenue(dblp)
    else:
       return True

    year = int(dblp['year'])

    if (year >= FIRST_YEAR) and (year <= LAST_YEAR) and (dblp_venue in confdata):

        venue, weight = confdata[dblp_venue]
        url = dblp['url']
        doi = getDOI(dblp['ee'])
        size = getPaperSize(url,dblp,doi)
        minimum_size = getMinPaperSize(weight)

        if size >= minimum_size:

           if url in black_list:
              return True

           title = getTitle(dblp['title'])

           if dblp_venue in manual_journals:
              if url in manual_classification:
                 m_area = manual_classification[url]
                 if m_area != area_prefix:
                    return True
              else:
                 write_mc_failed(year,dblp_venue,title,url)
                 return True

           found_paper = True;
           pid_papers.append(url)

           # this paper was already processed
           if (url in out):
              paper = out[url]
              if hasDept(paper[3],department):
                 return True
              else:
                 # but this author is from another department
                 paper2 = (paper[0], paper[1], paper[2], paper[3] + "; " + department,
                           paper[4], paper[5], paper[6], paper[7], paper[8],
                           paper[9])
                 out[url] = paper2
                 score[department] += inc_score(weight)
                 return True

           tier = getVenueTier(weight)
           venue_type = getVenueType(weight)
           arxiv = get_arxiv_url(doi,title)
           citations = get_citations(doi)
           authors = getAuthors(dblp['author'])

           out[url] = (year, venue, '"' + title + '"', department, authors, doi,
                        tier, venue_type, arxiv, citations)
           score[department] += inc_score(weight)

    return True

def get_dblp_file(pid,prof):
    prof = prof.replace(" ", "-")
    file = '../cache/dblp/' + prof + '.xml'
    if os.path.exists(file):
       with open(file) as f:
          bibfile = f.read()
    else:
       try:
         url = "http://dblp.org/pid/" + pid + ".xml"
         bibfile = requests.get(url).text
         with open(file, 'w') as f:
            f.write(bibfile.encode("UTF-8"))
       except requests.exceptions.RequestException as e:
         print e
         sys.exit(1)
    return bibfile

def outuput_everything():
    output_papers()
    output_scores()
    # output_profs()
    output_venues()
    output_profs_list()
    output_arxiv_cache(area_prefix)
    output_citations_cache(area_prefix)
    generate_search_box_list()
    if multi_area_journal:
       print  ALERT_ON + "Found papers in MULTI-AREA journals" + ALERT_OFF
    mc_failed_file.close()
    log.close()

def remove_prof_cache():
    prof_cache_pattern = "../cache/profs/" + area_prefix + "-*.csv"
    for f in glob.glob(prof_cache_pattern):
        os.remove(f)

# main program

area_prefix= sys.argv[1]
confs_file_name = area_prefix + "-confs.csv"

multi_area_journal = False

reader3 = csv.reader(open("research-areas-config.csv", 'r'))
for area_tuple in reader3:
  if area_tuple[0] == area_prefix:
     MIN_PAPER_SIZE = int(area_tuple[1])
     break

print "Research Area: " + area_prefix
print "Minimun paper size: " + str(MIN_PAPER_SIZE)

reader1 = csv.reader(open(confs_file_name, 'r'))
confdata = {}
conflist = []
journallist = []
for conf_row in reader1:
    conf_dblp, conf_name, conf_weight = conf_row
    confdata[conf_dblp]= conf_name, int(conf_weight)
    if int(conf_weight) <= 3:
       conflist.append(conf_name)
    else:
       journallist.append(conf_name)
conflist = list(set(conflist))  # removing duplicates
journallist = list(set(journallist))  # removing duplicates

out = {}
score = {}
profs = {}
profs_list = []

init_black_white_lists()
init_manual_files()
open_arxiv_cache(area_prefix)
open_citations_cache(area_prefix)
remove_prof_cache()

reader2 = csv.reader(open("all-researchers.csv", 'r'))
count = 1;
for researcher in reader2:

    prof_name = researcher[0]     # global variables
    department = researcher[1]
    pid = researcher[2]

    if not department in score:
       score[department] = 0.0
    if not department in profs:
       profs[department] = 0

    found_paper = False
    bibfile = get_dblp_file(pid,prof_name)
    pid_papers = []
    xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)

    if found_paper:
       profs_list.append((prof_name,department))
       profs[department] += 1
       print str(count) + " >> " + prof_name + ", " + department
       output_prof_papers(prof_name)
       merge_output_prof_papers(prof_name)

    count = count + 1;

outuput_everything()
