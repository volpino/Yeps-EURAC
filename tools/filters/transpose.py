#!/usr/bin/env python

from sys import argv
from numpy import *
import csv

try:
    input = argv[1]
    output = argv[2]
except IndexError:
    print "Usage: transpose.py <input> <output>"
    exit(1)

r = csv.reader(open(input), delimiter='\t')
w = csv.writer(open(output, 'w'), delimiter='\t')

mat = array([row for row in r], dtype=float)

for ts in mat.T:
    w.writerow(ts)
