# CSIndexbr: Exploring Brazilian Scientific Production in Computer Science

# By Marco Tulio Valente - ASERG/DCC/UFMG
# http://aserg.labsoft.dcc.ufmg.br


# How to use: python ../csdepts.py (from data folder)

import csv
import sys

dept_list = []
ranking = {}
num_prof_list = []
area_list = []

reader1 = csv.reader(open("research-areas-config.csv", 'r'))
for a in reader1:
    area_list.append(a[0])

reader3 = csv.reader(open("profs.csv", 'r'))
for a in reader3:
    num_prof_list.append(a[1])

for area in area_list:
    score = {}
    reader2 = csv.reader(open(area + "-out-scores.csv", 'r'))
    for dept_tuple in reader2:
        dept = dept_tuple[0]
        if not(dept in dept_list):
           dept_list.append(dept)
        s = float(dept_tuple[1])
        score[dept] = s
    ranking[area] = score

dept_list.sort()

f2 = open('depts/depts.html','w')
f2.write('<ul>\n')

for dept in dept_list:
    num_prof = num_prof_list.count(dept)
    if num_prof < 10:
       continue
    dept2 = dept.replace("/", "").replace(" ","").lower()
    f2.write('<li>  <a href="https://csindexbr.org/depts.html?d=' + dept2 + '">' + dept + '</a>\n')
    f = open('depts/scores-' + dept2 + '.csv','w')
    for area in area_list:
        f.write(area.upper())
        f.write(',')
        if dept in ranking[area]:
           f.write(str(ranking[area][dept]))
        else:
           f.write('0.00')
        f.write('\n')
    f.close()

f2.write('</ul>\n')
f2.close()
