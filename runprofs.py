import csv

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
    out.write('<li>  <a href="https://csindexbr.org/authors.html?p=' + p2 + '">')
    out.write(' ' + prof + '</a>')
    out.write(' <small> (' + dept + ') </small>')
    out.write('\n')
out.close
