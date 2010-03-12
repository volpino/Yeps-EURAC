from numpy import *
import csv

from sys import argv

try:
    format = argv[1]
    input1 = argv[2]
    input2 = argv[3]
    output = argv[4]
    mark   = argv[5]
except IndexError:
    print "Usage: cluster_plot.py <format> <input1> <input2> <output> <centroid>"
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
    l.append([float(i) for i in row])

centroidsid = array(l[:-1])
mini = array(l[-1])

r = csv.reader(open(input2), delimiter='\t')
mat = array([row for row in r], dtype=float)

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
        line = plt.plot(time_series, colours[i])
        if j == 0:
            lines.append(line)
    i += 1
plt.legend(lines, ["Cluster %d" % i for i, k in enumerate(clusters.keys())])

l = len(clusters.values()[0][0])
if l < 5:
    plt.xticks(range(l + 1), range(l + 1))

plt.ylabel("Intensity [a.u.]")
plt.xlabel("Time Points")

if mark == "y":
    for elem in centroidsid:
        plt.plot(elem, linewidth=1.5, color='black')

plt.savefig(output, format=format)
