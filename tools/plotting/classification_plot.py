from numpy import *
import csv
import iodata

from sys import argv

try:
    format = argv[1]
    labels_file = argv[2]
    ts_file = argv[3]
    output = argv[4]
except IndexError:
    print "Usage: cluster_plot.py <format> <input1> <input2> <output>"
    exit(1)

import matplotlib
if format == "png":
    matplotlib.use("Agg")
elif format == "pdf":
    matplotlib.use("PDF")
import matplotlib.pyplot as plt

labels_reader = csv.reader(open(labels_file), delimiter='\t')
labels = [row for row in labels_reader]

ts_reader = csv.reader(open(ts_file), delimiter='\t')
ts = [row for row in ts_reader]

colours = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']

set = {}
map(set.__setitem__, labels, [])
lbl = set.keys()

col = {}
for i, elem in enumerate(lbl):
    col[elem] = colours[i]

for n, t in enumerate(ts):
    plt.plot(t, col[labels[n]])
plt.ylabel(title)
plt.savefig(output, format=format)
