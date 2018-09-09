import csv
import sys

input_file = sys.argv[1]
col = int(sys.argv[2])

input = csv.reader(open(input_file, 'r'))

for line in input:
    print line[col]
