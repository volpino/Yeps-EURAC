from numpy import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv
import iodata

from sys import argv

try:
    input1 = argv[1]
    input2 = argv[2]
    output = argv[3]
except KeyError:
    print "Invalid input!"
    exit(1)

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
plt.savefig(output, format="png")
