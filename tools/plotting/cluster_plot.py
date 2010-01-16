from numpy import *
import csv
import iodata

from sys import argv

try:
    format = argv[1]
    input1 = argv[2]
    input2 = argv[3]
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

r = csv.reader(open(input1), delimiter='\t')
l = []
for row in r:
    l.append([int(i) for i in row])

centroidsid = array(l[0])
mini = array(l[1])

x, mat, header, title = iodata.load_csv(input2, '\t')

clusters = {}
i = 0
for c in mini:
    try:
        clusters[c].append(mat[i])
    except KeyError:
        clusters[c] = [mat[i]]
    i += 1

colours = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']
lines = []
i = 0
for key in clusters.keys():
    i = i % len(colours)
    for j, time_series in enumerate(clusters[key]):
        line = plt.plot(time_series, colours[i], label=key)
        if j == 0:
            lines.append(line)
    i += 1
plt.legend(lines)
plt.savefig(output, format=format)
