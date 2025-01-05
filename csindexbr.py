# pylint: disable=W0311,C0103,C0116,C0200,R1714

import csv
import re
import sys
import glob
import os
from difflib import SequenceMatcher
import requests
import xmltodict

FIRST_YEAR = 2020
LAST_YEAR = 2025

class Global:
    default_min_paper_size = 0
    black_list = {}    # list of papers that must not be counted (e.g., in invalid tracks)
    white_list = {}    # list of papers that must be counted (e.g., with missing page numbers)
    conflist = []      # conferences of the research area under processing
    journallist = []   # journals of the research area under processing
    out = {}           # list of papers already found in the research area under processing
    score = {}
    confdata = {}
    profs = {}
    profs_list = []
    arxiv_cache = {}
    manual_journals = {}
    manual_classification = {}
    pid_papers = []
    area_prefix = sys.argv[1]
    #multi_area_journal = False
    multi_area_journal_list = []
    mc_failed_file = open('manual-classification-failed.csv', 'a')

# functions for handling journals with manual classification

def init_manual_files():
    with open('manual-journals.txt') as mf:
         Global.manual_journals = mf.read().splitlines()
    reader = csv.reader(open('manual-classification.csv', 'r'))
    for row in reader:
        m_area, _, _, _, m_url = row
        Global.manual_classification[m_url] = m_area

def output_mc_failed(year, dblp_venue, title, url):
    if url in Global.multi_area_journal_list:
       return 
    #Global.multi_area_journal = True
    Global.multi_area_journal_list.append(url)
    file = Global.mc_failed_file
    file.write(",")
    file.write(str(year))
    file.write(",")
    file.write('"' + str(dblp_venue) + '"')
    file.write(",")
    file.write('"' + title + '"')
    file.write(",")
    file.write(str(url))
    file.write("\n")

def outuput_multi_area_journal():
    if Global.multi_area_journal_list:
       print('\033[94m' + "Found papers in MULTI-AREA journals" + '\033[0m')
    Global.mc_failed_file.close()

# arxiv-related functions

def init_arxiv_cache():
    fname = '../cache/arxiv/' + Global.area_prefix + '-arxiv-cache.csv'
    if os.path.exists(fname):
       reader = csv.reader(open(fname, 'r'))
       for line in reader:
           Global.arxiv_cache[line[0]] = line[1]

def output_arxiv_cache():
    if Global.arxiv_cache:
       f = open('../cache/arxiv/' + Global.area_prefix + '-arxiv-cache.csv', 'w')
       for doi in Global.arxiv_cache:
           f.write(doi)
           f.write(',')
           f.write(Global.arxiv_cache[doi])
           f.write('\n')
       f.close()

def get_arxiv_url(doi, title):
    if not isinstance(doi, str):
       return "no_arxiv"
    if doi in Global.arxiv_cache:
       return Global.arxiv_cache[doi]
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
    Global.arxiv_cache[doi] = arxiv_url
    return arxiv_url

# output functions

def outuput_everything():
    output_papers()
    output_scores()
    output_venues()
    output_profs_list()
    output_arxiv_cache()
    output_search_box_list()
    outuput_multi_area_journal()

def output_venues_confs(result):
    if len(result) > 0:
       f = open(Global.area_prefix + '-out-confs.csv', 'w')
       for conf in result:
           f.write(conf[0])
           f.write(',')
           f.write(str(conf[1]))
           f.write('\n')
       f.close()

def output_venues_journals(result):
    if len(result) > 0:
       f = open(Global.area_prefix + '-out-journals.csv', 'w')
       for journal in result:
           f.write(journal[0])
           f.write(',')
           f.write(str(journal[1]))
           f.write('\n')
       f.close()

def output_venues():
    confs = []
    journals = []
    for p in Global.out.items():
        if p[1][7] == "C":
           confs.append(p[1][1])
        else:
           journals.append(p[1][1])
    result1_temp = sorted([(c, confs.count(c)) for c in Global.conflist], key=lambda x: x[0])
    result1 = sorted(result1_temp, key=lambda x: x[1], reverse=True)
    result2_temp = sorted([(c, journals.count(c)) for c in Global.journallist], key=lambda x: x[0])
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
    out2 = sorted(Global.out.items(), key=lambda x: (x[1][1], x[1][2]))
    sorted_papers = sorted(out2, key=lambda x: x[1][0], reverse=True)
    f = open(Global.area_prefix + '-out-papers.csv', 'w')
    for i in range(0, len(sorted_papers)):
        paper = sorted_papers[i][1]
        write_paper(f, True, paper)
    f.close()

def output_prof_papers(prof):
    prof = prof.replace(" ", "-")
    f = open("../cache/profs/" + Global.area_prefix + "-" + prof + '-papers.csv', 'w')
    for url in Global.pid_papers:
        paper = Global.out[url]
        write_paper(f, False, paper)
    f.close()

def write_scores(sorted_scores):
    f = open(Global.area_prefix + '-out-scores.csv', 'w')
    for i in range(0, len(sorted_scores)):
        dept = sorted_scores[i][0]
        f.write(str(dept))
        f.write(',')
        s = round(sorted_scores[i][1], 2)
        f.write(str(s))
        f.write('\n')
    f.close()

def output_scores():
    final_score = {}
    for dept in Global.score:
        s = Global.score[dept]
        if s > 0:
            final_score[dept] = s
    sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
    sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)
    write_scores(sorted_scores)

def write_profs(sorted_profs):
    f = open(Global.area_prefix + '-out-profs.csv', 'w')
    for i in range(0, len(sorted_profs)):
        dept = sorted_profs[i][0]
        f.write(str(dept))
        f.write(',')
        s = sorted_profs[i][1]
        f.write(str(s))
        f.write('\n')
    f.close()

def output_profs():
    final_profs = {}
    for dept in Global.profs:
        s = Global.profs[dept]
        if s > 0:
           final_profs[dept] = s
    sorted_profs_temp = sorted(final_profs.items(), key=lambda x: x[0])
    sorted_profs = sorted(sorted_profs_temp, key=lambda x: x[1], reverse=True)
    if len(sorted_profs) >= 16:
       sorted_profs = sorted_profs[:16]
    write_profs(sorted_profs)

def output_profs_list():
    profs = Global.profs_list
    profs = sorted(profs, key=lambda x: x[0])
    f = open(Global.area_prefix + '-out-profs-list.csv', 'w')
    for i in range(0, len(profs)):
        f.write(str(profs[i][0]))
        f.write(',')
        f.write(str(profs[i][1]))
        f.write('\n')
    f.close()

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

def output_search_box_list():
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

# dblp parsing auxiliary functions

def get_paper_score(weight):
    if (weight == 1) or (weight == 4):
       return 1.0
    if weight == 2:
       return 0.66
    if (weight == 3) or (weight == 6) or (weight == 7):
       return 0.33
    if weight == 5:
       return 0.4
    return 0.0

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

def get_min_paper_size(weight):
    if weight == 6:  # magazine
       return 6
    if (weight == 4) or (weight == 5) or (weight == 7): # journals
       return 0   # due to missing page numbers in Elsevier journals
    return Global.default_min_paper_size   # conferences

def as_int(i):
    try:
       return int(i)
    except:
       return 0

def parse_paper_size(dblp_pages):
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

def get_paper_size(url, dblp, dblp_venue):
    if url in Global.white_list:
       return 10
    if 'pages' in dblp:
       return parse_paper_size(dblp['pages'])
    if (dblp_venue == "Briefings Bioinform.") or \
       (dblp_venue == "NeurIPS"):
       return 10    # due to missing page fields
    return 0

def get_dblp_venue(dblp):
    if 'journal' in dblp:
        if (dblp['journal'] == "PACMPL") or \
           (dblp['journal'] == "PACMHCI") or \
           (dblp['journal'] == "Proc. ACM Program. Lang.") or \
           (dblp['journal'] == "Proc. ACM Softw. Eng.") or \
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

def has_dept(dept_str, dept):
    dept_list = dept_str.split(";")
    for d in dept_list:
        d = d.replace(" ", "")
        if d == dept:
           return True
    return False

def is_manual_journal(year, dblp_venue, title, url):
    if dblp_venue in Global.manual_journals:
       if url in Global.manual_classification:
          m_area = Global.manual_classification[url]
          if m_area != Global.area_prefix:
             return True
       else:
          output_mc_failed(year, dblp_venue, title, url)
          return True
    return False

# main dblp parse function

def is_paper_size_ok(url, dblp, dblp_venue, weight):
    size = get_paper_size(url, dblp, dblp_venue)
    minimum_size = get_min_paper_size(weight)
    return size >= minimum_size

def update_paper(paper, dept, url, weight):
    Global.out[url] = (paper[0], paper[1], paper[2], paper[3] + "; " + dept,
                       paper[4], paper[5], paper[6], paper[7], paper[8],
                       paper[9])
    Global.score[dept] += get_paper_score(weight)

def add_new_paper(weight, doi, title, dblp, url, year, venue, global_department):
    tier = get_venue_tier(weight)
    venue_type = get_venue_type(weight)
    arxiv = get_arxiv_url(doi, title)
    citations = 0
    authors = get_authors(dblp['author'])
    Global.out[url] = (year, venue, '"' + title + '"', global_department, authors, doi,
                          tier, venue_type, arxiv, citations)
    Global.score[global_department] += get_paper_score(weight)
    
def is_paper_indexable(dblp):
    if not isinstance(dblp, dict):
       return False
    if ('journal' in dblp) or ('booktitle' in dblp):
       dblp_venue = get_dblp_venue(dblp)
       year = int(dblp['year'])
       if (year >= FIRST_YEAR) and (year <= LAST_YEAR) and (dblp_venue in Global.confdata):
          _, weight = Global.confdata[dblp_venue]
          url = dblp['url']
          if url in Global.black_list:
             return False
          title = get_title(dblp['title'])
          if is_manual_journal(year, dblp_venue, title, url):
             return False
          return is_paper_size_ok(url, dblp, dblp_venue, weight)
    return False

def parse_dblp(_, dblp):
    global global_department, global_found_paper

    if is_paper_indexable(dblp):
       dblp_venue = get_dblp_venue(dblp)
       year = int(dblp['year'])
       venue, weight = Global.confdata[dblp_venue]
       url = dblp['url']
       doi = get_doi(dblp['ee'])
       title = get_title(dblp['title'])

       global_found_paper = True   # global variable
       Global.pid_papers.append(url)

       if url in Global.out:  # already processed paper
          paper = Global.out[url]
          if has_dept(paper[3], global_department):
             return True
          update_paper(paper, global_department, url, weight)
          return True
       
       add_new_paper(weight, doi, title, dblp, url, year, venue, global_department)
    
    return True   # True = continue parsing next paper

# init functions

def init_black_list():
    black_list_file = Global.area_prefix + "-black-list.txt"
    if os.path.exists(black_list_file):
       with open(black_list_file) as blf:
         Global.black_list = blf.read().splitlines()

def init_white_list():
    white_list_file = Global.area_prefix + "-white-list.txt"
    if os.path.exists(white_list_file):
       with open(white_list_file) as wlf:
         Global.white_list = wlf.read().splitlines()

def init_prof_cache():
    prof_cache_pattern = "../cache/profs/" + Global.area_prefix + "-*.csv"
    for f in glob.glob(prof_cache_pattern):
        os.remove(f)

def init_confs():
    reader = csv.reader(open(Global.area_prefix + "-confs.csv", 'r'))
    for conf_row in reader:
        conf_dblp, conf_name, conf_weight = conf_row
        Global.confdata[conf_dblp] = conf_name, int(conf_weight)
        if int(conf_weight) <= 3:
           Global.conflist.append(conf_name)
        else:
           Global.journallist.append(conf_name)
    Global.conflist = list(set(Global.conflist))  # removing duplicates
    Global.journallist = list(set(Global.journallist))  # removing duplicates

def init_min_paper_size():
    reader = csv.reader(open("research-areas-config.csv", 'r'))
    for area_tuple in reader:
        if area_tuple[0] == Global.area_prefix:
           Global.default_min_paper_size = int(area_tuple[1])
           break

def init_everything():
    init_min_paper_size()
    init_confs()
    init_black_list()
    init_white_list()
    init_manual_files()
    init_arxiv_cache()
    init_prof_cache()

# main loop that process each researcher

def read_dblp_file(pid, prof):
    prof = prof.replace(" ", "-")
    file = '../cache/dblp/' + prof + '.xml'
    if os.path.exists(file):
       with open(file) as f:
          dblp_xml = f.read()
    else:
       try:
          url = "http://dblp.org/pid/" + pid + ".xml"
          dblp_xml = requests.get(url).text
          with open(file, 'w') as f:
             f.write(str(dblp_xml))
       except requests.exceptions.RequestException as e:
          print(e)
          sys.exit(1)
    return dblp_xml

def process_prof_with_paper(prof, dept):
    Global.profs_list.append((prof, dept))
    Global.profs[dept] += 1
    output_prof_papers(prof)
    merge_output_prof_papers(prof)

def process_department_data(dept):
    if not dept in Global.score:
       Global.score[dept] = 0.0
    if not dept in Global.profs:
       Global.profs[dept] = 0

def process_all_researchers():
    global global_department, global_found_paper
    all_researchers = csv.reader(open("all-researchers.csv", 'r'))
    count = 1
    print("Research Area: " + Global.area_prefix)
    for researcher in all_researchers:
        prof = researcher[0]
        global_department = researcher[1]   # global
        pid = researcher[2]
        process_department_data(global_department)
        bibfile = read_dblp_file(pid, prof)
        Global.pid_papers = []
        global_found_paper = False    # global
        xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)
        if global_found_paper:
           process_prof_with_paper(prof, global_department)
           print(str(count) + " >> " + prof + ", " + global_department)
        count = count + 1

# main program

init_everything()
process_all_researchers()
outuput_everything()
