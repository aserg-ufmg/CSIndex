import csv
import sys

def toInt(str):
    if str == '':
       return 0
    else:
       return int(str)

allpapers = csv.reader(open(sys.argv[1]))
allpapers = sorted(allpapers, key=lambda row: toInt(row[9]), reverse=True)
f = open('trending.csv','w')
i = 0
for paper in allpapers:
    for j in range(0,10):
        f.write(str(paper[j]))
        if j < 9:
           f.write(',')
        else:
           f.write('\n')
    i = i + 1
    if (i == 15):
       break
f.close()
