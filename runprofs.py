import csv
import glob

def file_size(file):
    num_lines = sum(1 for line in open(file))
    return num_lines

def get_area(prof):
    size = 0
    area = ""
    for file in glob.glob("../cache/profs/*" + prof + "-papers.csv"):
        size2 = file_size(file)
        if size2 > size:
           size = size2
           area = file[15:file.index('-')]
    return area.upper()

inst = {}
reader1 = csv.reader(open("all-researchers.csv", 'r'))
for p in reader1:
    prof = p[0]
    dept = p[1]
    inst[prof] = dept

out = open('../profs.html','a')
reader2 = csv.reader(open("./profs/all-authors.csv", 'r'))
for p in reader2:
    prof = p[0]
    p2 = prof.replace(" ", "-")
    dept = inst[prof]
    area = get_area(p2)
    out.write('<li>  <a href="https://csindexbr.org/authors.html?p=' + p2 + '">')
    out.write(' ' + prof + '</a>')
    out.write(' <small> (' + dept + ', ' + area + ') </small>')
    out.write('\n')

out.close
