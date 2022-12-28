
# IMPORTANT: Citations are now disabled

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
    # citations are now disabled
    return 0   

    if doi in citations_cache:
       return citations_cache[doi]
    doi_full = doi
    i = doi_full.find("10.")
    if i == -1:
       return -1
    doi = doi_full[i:]
    url = "https://api.crossref.org/works/" + doi
    try:
      r = requests.get(url, headers=headers)
      doi_json = json.loads(r.text)
      citations = doi_json["message"]["is-referenced-by-count"]
      citations_cache[doi_full] = citations
      time.sleep(4)
      return citations
    except:
      return -1
