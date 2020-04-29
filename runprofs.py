import csv
import glob
import os

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

def create_p_file(prof_name):
   file_name = "../p/" + prof_name + '.html'
   if os.path.exists(file_name):
      return
   line = '      var corebr_author = "' + prof_name + '"\n'
   out = open(file_name, 'w')
   file1 = open('../_authors1.html', 'r')
   file2 = open('../_authors2.html', 'r')
   out.write(file1.read())
   out.write(line)
   out.write(file2.read())
   out.close

inst = {}
reader1 = csv.reader(open("all-researchers.csv", 'r'))
for p in reader1:
    prof = p[0]
    dept = p[1]
    inst[prof] = dept

out = open('../profs.html','a')
out2 = open('profs.csv','w')
# out3 = open('../html/sitemap_p.txt','w')
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

    out2.write(prof)
    out2.write(',')
    out2.write(dept)
    out2.write(',')
    out2.write(area)
    out2.write('\n')
    #create_p_file(p2)
#    out3.write('https://csindexbr.org/authors.html?p=' + p2 + '\n')
out.close
out2.close
#out3.close
