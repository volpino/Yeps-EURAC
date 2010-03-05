#!/usr/bin/env python

from sys import argv
import csv

try:
    input = argv[1]
    col = argv[2]
    out1 = argv[3]
    out2 = argv[4]
except IndexError:
    print "Usage: extract_labels.py <input> <output1> <output2>"
    exit(1)
try:
    col = int(col)
except ValueError:
    print "Invalid column id!"
    exit(1)

r = csv.reader(open(input), delimiter='\t')
w1 = csv.writer(open(out1, 'w'), delimiter='\t')
w2 = open(out2, 'w')

content = [row for row in r]

for line in [row[col] for row in content]:
    w2.write("%s\n" % line)

for line in content:
    del line[col]
    w1.writerow(line)
