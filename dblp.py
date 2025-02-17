# How to use (from data folder):
# python ../dblp.py
# python ../dblp.py -test (only test the cached files)

import os
import sys
import time
import csv
import requests
import xmltodict

def is_in_cache(prof):
    file = '../cache/dblp/' + prof + '.xml'
    return os.path.exists(file)
   
def save_cache(prof, bibfile):
    file = '../cache/dblp/' + prof + '.xml'  
    with open(file, 'w') as f:
      f.write(str(bibfile))
      
def read_cache(prof):
    file = '../cache/dblp/' + prof + '.xml'  
    with open(file) as f:
      return f.read()

def crawl_dblp(pid):
    try:
      url = "http://dblp.org/pid/" + pid + ".xml"
      return requests.get(url, timeout=180).text
    except requests.Timeout:
      print("Request timed out after 180 seconds")     
    except requests.exceptions.RequestException as e:
      print (e)
      sys.exit(1)
   
def get_dblp_file(pid, prof):
    # prof = prof.replace(" ", "-")
    if is_in_cache(prof):
       return read_cache(prof)
    else:
       return crawl_dblp(pid)

def parse_dblp(_, dblp):
    if ('journal' in dblp) or ('booktitle' in dblp):
       return True
    return True

def download_all_prof_data():
    start_time = time.time()
    reader = csv.reader(open("all-researchers.csv", 'r'))
    count = 1;
    for researcher in reader:
        prof, department, pid = researcher
        print(f"{count} > {prof}, {department}")
        prof = prof.replace(" ", "-")
       
        bibfile = get_dblp_file(pid, prof)
        save_cache(prof, bibfile)

        time.sleep(2)
        count = count + 1
    elapsed_time = round((time.time() - start_time) / 60, 2)
    print(f"Elapsed time (min): {elapsed_time}")

def test_all_prof_data():
    print ("Testing files ....")
    reader = csv.reader(open("all-researchers.csv", 'r'))
    count = 1;
    for researcher in reader:
        prof, department, pid = researcher
        print(f"{count} > {prof}, {department}")
        prof = prof.replace(" ", "-")
        bibfile = get_dblp_file(pid, prof)
        xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)
        count = count + 1

if __name__ == "__main__":
    download = len(sys.argv) < 2 or sys.argv[1] != "-test"
    if download:
       download_all_prof_data()
    test_all_prof_data()
    