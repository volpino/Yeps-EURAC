#!/usr/bin/env python

from sys import argv
import csv
import random

try:
    input = argv[1]
    output1 = argv[2]
    output2 = argv[3]
except IndexError:
    print "Usage: split_dataset.py <input> <output1> <output2>"
    exit(1)

reader = csv.reader(open(input), delimiter='\t')
l1 = [row for row in reader]
l2 = []

for i in range(len(l1) / 3):
    n = random.randint(0, len(l1) / 3)
    l2.append(l1[n])
    del l1[n]

w1 = csv.writer(open(output1, 'w'), delimiter='\t')
for i in l1:
    w1.writerow(i)

w2 = csv.writer(open(output2, 'w'), delimiter='\t')
for i in l2:
    w2.writerow(i)
