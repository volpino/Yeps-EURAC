from numpy import *
import csv

from sys import argv

try:
    format = argv[1]
    labels_file = argv[2]
    ts_file = argv[3]
    output = argv[4]
except IndexError:
    print "Usage: classification_plot.py <format> <input1> <input2> <output>"
    exit(1)

import matplotlib
if format == "png":
    matplotlib.use("Agg")
elif format == "pdf":
    matplotlib.use("PDF")
import matplotlib.pyplot as plt

labels_reader = csv.reader(open(labels_file), delimiter='\t')
labels = [row[0] for row in labels_reader]

ts_reader = csv.reader(open(ts_file), delimiter='\t')
ts = [row for row in ts_reader]

colours = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']

col = {}
i = 0
for k, elem in enumerate(labels):
    if not col.has_key(elem):
        col[elem] = (i, colours[i%len(colours)])
        i += 1
l=[]
for n, t in enumerate(ts):
    l.append(plt.plot(t, col[labels[n]][1], label=labels[n]))

if len(ts[0][1]) < 5:
    plt.xticks(range(len(ts[0][1]) + 1), range(len(ts[0][1]) + 1))

plt.ylabel("Intensity [a.u.]")
plt.xlabel("Time Points")
plt.savefig(output, format=format)


plt.legend([l[labels.index(k)] for k in col.keys()], col.keys())
plt.savefig(output, format=format)
