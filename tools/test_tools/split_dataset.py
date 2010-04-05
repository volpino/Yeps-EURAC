#!/usr/bin/env python

from sys import argv
import csv
import random

try:
    input = argv[1]
    col = argv[2]
    output1 = argv[3]
    output2 = argv[4]
except IndexError:
    print "Usage: split_dataset.py <input> <output1> <output2>"
    exit(1)

reader = csv.reader(open(input), delimiter='\t')
l1 = [row for row in reader]
l2 = []

if col != 'None': 
    try:
        col = int(col)
    except ValueError:
        print "Invalid column id!"
        exit(1)
    labels = []
    labeli_index = []
    l2_index = []
    for i in range(len(l1)):
        if (l1[i][col] in labels) == False:
            labels.append(l1[i][col])
            labeli_index.append([])
        else:
            continue
    for i in range(len(labels)):
        for j in range(len(l1)):
            if l1[j][col] == labels[i]:
                labeli_index[i].append(j)
            else:
                continue
    for i in range(len(labeli_index)):
        if len(labeli_index[i]) / 3 < 1:
            l2_index.append(label_index[i][random.randint(0, len(label_index[i]) - 1)])
        else:
            used_r = []
            for j in range(len(labeli_index[i]) / 3):           # could be done by canceling things out
                r = random.randint(0, len(labeli_index[i]) -1)
                if (r in used_r) == False:
                    l2_index.append(labeli_index[i][r])
                    used_r.append(r)
                else:
                    j = j - 1
    for i in range(len(l2_index)):
        if l2_index.count(l2_index[i]) > 1:
            del l2_index[i]
        else:
            continue
    l2_index.sort()
    l2_index.reverse()
    for i in range(len(l2_index)):
        l2.append(l1[l2_index[i]])
        del l1[l2_index[i]]
        
else:
    for i in range(len(l1) / 3):
        n = random.randint(0, len(l1) -1 - i)
        l2.append(l1[n])
        del l1[n]

w1 = csv.writer(open(output1, 'w'), delimiter='\t')
for i in l1:
    w1.writerow(i)

w2 = csv.writer(open(output2, 'w'), delimiter='\t')
for i in l2:
    w2.writerow(i)
