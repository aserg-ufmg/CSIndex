import csv
import sys

# python getcol.py [file-name] [col1] [col2]

input_file = sys.argv[1]
col1 = int(sys.argv[2])
col2 = int(sys.argv[3])

input = csv.reader(open(input_file, 'r'))

for line in input:
    print line[col1] + '  '+ line[col2]
