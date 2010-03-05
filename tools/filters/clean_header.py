#!/usr/bin/env python

from sys import argv
import csv
import iodata

try:
    input = argv[1]
    output = argv[2]
except IndexError:
    print "Usage: clean_header.py <input> <output>"
    exit(1)

x, mat, header, title = iodata.load_csv(input, '\t')

w = csv.writer(open(output, 'w'), delimiter='\t')
for ts in mat:
    w.writerow(ts)

