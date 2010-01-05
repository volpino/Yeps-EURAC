from numpy import *
import csv
import iodata

from sys import argv

try:
    format = argv[1]
    input1 = argv[2]
    input2 = argv[3]
    output = argv[4]
except KeyError:
    print "Invalid input!"
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
colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
i = 0
for cluster in clusters.values():
    i = i % len(colours)
    for time_series in cluster:
        line = plt.plot(time_series)
        plt.setp(line, color=colours[i])
    i += 1
plt.ylabel(title)
plt.savefig(output, format=format)
