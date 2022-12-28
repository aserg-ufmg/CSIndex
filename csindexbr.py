# pylint: disable=W0311,C0103,C0116

import csv
import re
import sys
import glob
import os
from difflib import SequenceMatcher
import requests
import xmltodict

FIRST_YEAR = 2018
LAST_YEAR = 2023

#################################################

# black-list: papers that must not be counted (e.g., in invalid tracks)
# white-list: papers that must be counted (e.g., with missing page numbers)
black_list = {}
white_list = {}

def init_black_white_lists():
    global black_list, white_list

    black_list_file = area_prefix + "-black-list.txt"
    if os.path.exists(black_list_file):
       with open(black_list_file) as blf:
         black_list = blf.read().splitlines()

    white_list_file = area_prefix + "-white-list.txt"
    if os.path.exists(white_list_file):
       with open(white_list_file) as wlf:
         white_list = wlf.read().splitlines()

#################################################

manual_journals = {}
manual_classification = {}
mc_failed_file = open('manual-classification-failed.csv', 'a')

def init_manual_files():
    global manual_journals, manual_classification
    with open('manual-journals.txt') as mf:
         manual_journals = mf.read().splitlines()
    reader = csv.reader(open('manual-classification.csv', 'r'))
    for row in reader:
        m_area, m_year, m_venue, m_title, m_url = row
        manual_classification[m_url] = m_area

def open_arxiv_cache(area):
    global arxiv_cache
    arxiv_cache = {}
    fname = '../cache/arxiv/' + area + '-arxiv-cache.csv'
    if os.path.exists(fname):
       reader = csv.reader(open(fname, 'r'))
       for line in reader:
           arxiv_cache[line[0]] = line[1]

def output_arxiv_cache(area):
    if arxiv_cache:  # global
       f = open('../cache/arxiv/' + area + '-arxiv-cache.csv', 'w')
       for doi in arxiv_cache:
           f.write(doi)
           f.write(',')
           f.write(arxiv_cache[doi])
           f.write('\n')
       f.close()

def get_arxiv_url(doi, title):
    if not isinstance(doi, str):
       return "no_arxiv"
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
          if SequenceMatcher(None, t1, t2).ratio() >= 0.9:
             arxiv_url = arxiv["id"]
    except:
        arxiv_url = "no_arxiv"
    arxiv_cache[doi] = arxiv_url
    return arxiv_url

#################################################

def as_int(i):
    try:
       return int(i)
    except:
       return 0

def paper_size(dblp_pages):
    page = re.split(r"-|:", dblp_pages)
    if len(page) == 2:
       p1 = as_int(page[0])
       p2 = as_int(page[1])
       return p2 - p1 + 1
    if len(page) == 4:
       p1 = as_int(page[1])
       p2 = as_int(page[3])
       return int(p2) - int(p1) + 1
    if len(page) == 3:
       p1 = as_int(page[1])
       p2 = as_int(page[2])
       return int(p2) - int(p1) + 1
    return 0

#################################################

def output_venues_confs(result):
    if len(result) > 0:
       f = open(area_prefix + '-out-confs.csv', 'w')
       for conf in result:
           f.write(conf[0])
           f.write(',')
           f.write(str(conf[1]))
           f.write('\n')
       f.close()

def output_venues_journals(result):
    if len(result) > 0:
       f = open(area_prefix + '-out-journals.csv', 'w')
       for journal in result:
           f.write(journal[0])
           f.write(',')
           f.write(str(journal[1]))
           f.write('\n')
       f.close()

def output_venues():
    global out, conflist, journallist
    confs = []
    journals = []
    for p in out.items():
        if p[1][7] == "C":
           confs.append(p[1][1])
        else:
           journals.append(p[1][1])
    result1_temp = sorted([(c, confs.count(c)) for c in conflist], key=lambda x: x[0])
    result1 = sorted(result1_temp, key=lambda x: x[1], reverse=True)
    result2_temp = sorted([(c, journals.count(c)) for c in journallist], key=lambda x: x[0])
    result2 = sorted(result2_temp, key=lambda x: x[1], reverse=True)
    output_venues_confs(result1)
    output_venues_journals(result2)

def write_paper(f, is_prof_tab, paper):
    f.write(str(paper[0]))
    f.write(',')
    f.write(str(paper[1]))
    f.write(',')
    f.write(str(paper[2]))
    f.write(',')
    if is_prof_tab:
       f.write(str(paper[3]))  # department
       f.write(',')
    authors = paper[4]
    for author in authors[:-1]:
        f.write(str(author))
        f.write('; ')
    f.write(str(authors[-1]))
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
    out2 = sorted(out.items(), key=lambda x: (x[1][1], x[1][2]))
    sorted_papers = sorted(out2, key=lambda x: x[1][0], reverse=True)
    f = open(area_prefix + '-out-papers.csv', 'w')
    for i in range(0, len(sorted_papers)):
        paper = sorted_papers[i][1]
        write_paper(f, True, paper)
    f.close()

def output_prof_papers(prof):
    prof = prof.replace(" ", "-")
    f = open("../cache/profs/" + area_prefix + "-" + prof + '-papers.csv', 'w')
    for url in pid_papers:
        paper = out[url]
        write_paper(f, False, paper)
    f.close()

def output_scores():
  global score

  final_score = {}
  for dept in score:
      s = score[dept]
      if s > 0:
         final_score[dept] = s

  sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
  sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)

  f = open(area_prefix + '-out-scores.csv', 'w')
  for i in range(0, len(sorted_scores)):
      dept = sorted_scores[i][0]
      f.write(str(dept))
      f.write(',')
      s = round(sorted_scores[i][1], 2)
      f.write(str(s))
      f.write('\n')
  f.close()

def output_profs():
  global profs

  final_profs = {}
  for dept in profs:
      s = profs[dept]
      if s > 0:
         final_profs[dept] = s

  sorted_profs_temp = sorted(final_profs.items(), key=lambda x: x[0])
  sorted_profs = sorted(sorted_profs_temp, key=lambda x: x[1], reverse=True)
  if len(sorted_profs) >= 16:
     sorted_profs = sorted_profs[:16]

  f = open(area_prefix + '-out-profs.csv', 'w')
  for i in range(0, len(sorted_profs)):
      dept = sorted_profs[i][0]
      f.write(str(dept))
      f.write(',')
      s = sorted_profs[i][1]
      f.write(str(s))
      f.write('\n')
  f.close()

def output_profs_list(area, profs):
    profs = sorted(profs, key=lambda x: x[0])
    f = open(area + '-out-profs-list.csv', 'w')
    for i in range(0, len(profs)):
        f.write(str(profs[i][0]))
        f.write(',')
        f.write(str(profs[i][1]))
        f.write('\n')
    f.close()

def remove_prof_papers_file(area, prof):
    prof = prof.replace(" ", "-")
    file = "../cache/profs/" + area + "-" + prof + '-papers.csv'
    if os.path.exists(file):
       print("Removing "+ file)
       os.remove(file)

def file_len(file):
    with open(file) as f:
       for i, l in enumerate(f):
           pass
    return i + 1

def flush_prof_papers(area, prof):
    num_lines = 0
    prof = prof.replace(" ", "-")
    file = "../cache/profs/" + area + "-" + prof + '-papers.csv'
    if os.path.exists(file):
       num_lines = file_len(file)
       os.remove(file)
    return num_lines

def merge_output_prof_papers(prof):
    os.chdir("../cache/profs")
    filenames = []
    prof = prof.replace(" ", "-")
    for file in glob.glob("*" + prof + "-papers.csv"):
        filenames.append(file)
    filenames.sort()
    outfile = open("../../data/profs/search/" + prof + ".csv", 'w')
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
    f = open("../all-authors.csv", 'w')
    for p in profs:
        f.write(p)
        f.write('\n')
    f.close()

def inc_score(weight):
    if (weight == 1) or (weight == 4):
       return 1.0
    if weight == 2:
       return 0.66
    if (weight == 3) or (weight == 6) or (weight == 7):
       return 0.33
    if weight == 5:
       return 0.4
    return 0.0

def get_min_paper_size(weight):
    if weight == 6:  # magazine
       return 6
    if (weight == 4) or (weight == 5) or (weight == 7): # journals
       return 0   # due to missing page numbers in Elsevier journals
    return default_min_paper_size   # conferences

def get_doi(doi):
    if isinstance(doi, list):
       doi = doi[0]
    if isinstance(doi, dict):
       doi = doi["#text"]
    return doi

def get_venue_tier(weight):
    if (weight == 1) or (weight == 4):
       return "top"
    if weight == 2:
       return "near-top"
    return "null"

def get_venue_type(weight):
    if weight <= 3:
       return "C"
    return "J"

def get_authors(author_list):
    authors = []
    if isinstance(author_list, dict): # single author paper
       author_list = author_list["#text"]
       authors.append(author_list)
    elif isinstance(author_list, str):  # single author paper
       if isinstance(author_list, dict):
          author_list = author_list["#text"]
       authors.append(author_list)
    else:
       for name in author_list:
           if isinstance(name, dict):
              name = name["#text"]
           authors.append(name)
    return authors

def get_title(title):
    if isinstance(title, dict):
       return title["#text"]
    return title.replace("\"", "")  # remove quotes in titles

def get_paper_size(url, dblp, dblp_venue):
    if url in white_list:
       return 10
    if 'pages' in dblp:
       return paper_size(dblp['pages'])
    if dblp_venue == "Briefings Bioinform.":
       return 10    # exception due to missing page fields
    return 0

def get_dblp_venue(dblp):
    if 'journal' in dblp:
        if (dblp['journal'] == "PACMPL") or (dblp['journal'] == "PACMHCI") or \
           (dblp['journal'] == "Proc. ACM Program. Lang.") or \
           (dblp['journal'] == "Proc. ACM Hum. Comput. Interact."):
           if 'number' in dblp:
              dblp_venue = dblp['number']
           else:
              dblp_venue = dblp['journal']
        else:
           dblp_venue = dblp['journal']
    elif 'booktitle' in dblp:
           dblp_venue = dblp['booktitle']
    else:
       print("Failed parsing DBLP")
       sys.exit(1)
    return dblp_venue

def output_mc_failed(year, dblp_venue, title, url):
    global mc_failed_file, multi_area_journal
    mc_failed_file.write(",")
    mc_failed_file.write(str(year))
    mc_failed_file.write(",")
    mc_failed_file.write('"' + str(dblp_venue) + '"')
    mc_failed_file.write(",")
    mc_failed_file.write('"' + title + '"')
    mc_failed_file.write(",")
    mc_failed_file.write(str(url))
    mc_failed_file.write("\n")
    multi_area_journal = True

def has_dept(dept_str, dept):
    dept_list = dept_str.split(";")
    for d in dept_list:
        d = d.replace(" ", "")
        if d == dept:
           return True
    return False

def parse_dblp(_, dblp):
    global department, found_paper, black_list

    if not isinstance(dblp, dict):
       return True
    if ('journal' in dblp) or ('booktitle' in dblp):
       dblp_venue = get_dblp_venue(dblp)
    else:
       return True
    year = int(dblp['year'])

    if (year >= FIRST_YEAR) and (year <= LAST_YEAR) and (dblp_venue in confdata):
        venue, weight = confdata[dblp_venue]
        url = dblp['url']
        doi = get_doi(dblp['ee'])
        size = get_paper_size(url, dblp, dblp_venue)
        minimum_size = get_min_paper_size(weight)

        if size >= minimum_size:

           if url in black_list:
              return True
           title = get_title(dblp['title'])

           if dblp_venue in manual_journals:
              if url in manual_classification:
                 m_area = manual_classification[url]
                 if m_area != area_prefix:
                    return True
              else:
                 output_mc_failed(year, dblp_venue, title, url)
                 return True

           found_paper = True
           pid_papers.append(url)

           # paper was already processed
           if url in out:
              paper = out[url]
              if has_dept(paper[3], department):
                 return True
              # author is from another department
              out[url] = (paper[0], paper[1], paper[2], paper[3] + "; " + department,
                          paper[4], paper[5], paper[6], paper[7], paper[8],
                          paper[9])
              score[department] += inc_score(weight)
              return True

           tier = get_venue_tier(weight)
           venue_type = get_venue_type(weight)
           arxiv = get_arxiv_url(doi, title)
           citations = 0  # get_citations(doi) is disabled
           authors = get_authors(dblp['author'])

           out[url] = (year, venue, '"' + title + '"', department, authors, doi,
                       tier, venue_type, arxiv, citations)
           score[department] += inc_score(weight)

    return True

def get_dblp_file(dblp_pid, prof):
    prof = prof.replace(" ", "-")
    file = '../cache/dblp/' + prof + '.xml'
    if os.path.exists(file):
       with open(file) as f:
          dblp_xml = f.read()
    else:
       try:
          url = "http://dblp.org/pid/" + dblp_pid + ".xml"
          dblp_xml = requests.get(url).text
          with open(file, 'w') as f:
             f.write(str(dblp_xml))
       except requests.exceptions.RequestException as e:
          print(e)
          sys.exit(1)
    return dblp_xml

def outuput_multi_area_journal():
    if multi_area_journal:
       print('\033[94m' + "Found papers in MULTI-AREA journals" + '\033[0m')
    mc_failed_file.close()

def outuput_everything():
    output_papers()
    output_scores()
    output_venues()
    output_profs_list(area_prefix, profs_list)
    output_arxiv_cache(area_prefix)
    generate_search_box_list()
    outuput_multi_area_journal()

def remove_prof_cache():
    prof_cache_pattern = "../cache/profs/" + area_prefix + "-*.csv"
    for f in glob.glob(prof_cache_pattern):
        os.remove(f)

def init_confs():
    global confdata, conflist, journallist
    reader = csv.reader(open(confs_file_name, 'r'))
    for conf_row in reader:
        conf_dblp, conf_name, conf_weight = conf_row
        confdata[conf_dblp] = conf_name, int(conf_weight)
        if int(conf_weight) <= 3:
           conflist.append(conf_name)
        else:
           journallist.append(conf_name)
    conflist = list(set(conflist))  # removing duplicates
    journallist = list(set(journallist))  # removing duplicates

def init_min_paper_size():
    global default_min_paper_size
    reader = csv.reader(open("research-areas-config.csv", 'r'))
    for area_tuple in reader:
        if area_tuple[0] == area_prefix:
           default_min_paper_size = int(area_tuple[1])
           break


# main program

area_prefix = sys.argv[1]
confs_file_name = area_prefix + "-confs.csv"
multi_area_journal = False
default_min_paper_size = 0
init_min_paper_size()

print("Research Area: " + area_prefix)
print("Minimun paper size: " + str(default_min_paper_size))

confdata = {}
conflist = []
journallist = []
init_confs()

out = {}
score = {}
profs = {}
profs_list = []

init_black_white_lists()
init_manual_files()
open_arxiv_cache(area_prefix)
remove_prof_cache()

all_researchers = csv.reader(open("all-researchers.csv", 'r'))
count = 1
for researcher in all_researchers:
    prof_name = researcher[0]     # global variables
    department = researcher[1]
    pid = researcher[2]

    if not department in score:
       score[department] = 0.0
    if not department in profs:
       profs[department] = 0

    found_paper = False
    bibfile = get_dblp_file(pid, prof_name)
    pid_papers = []

    xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)

    if found_paper:
       profs_list.append((prof_name, department))
       profs[department] += 1
       print(str(count) + " >> " + prof_name + ", " + department)
       output_prof_papers(prof_name)
       merge_output_prof_papers(prof_name)

    count = count + 1

outuput_everything()
