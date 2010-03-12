#!/usb/bin/env python

from sys import argv
import csv
import numpy as np

try:
    sep = argv[1]
    format = argv [2]
    input = argv[3]
    output = argv[4]
except IndexError:
    print "Usage: script <separator> <format> <input> <output>"
    exit(1)

import matplotlib
if format == "png":
    matplotlib.use("Agg")
elif format == "pdf":
    matplotlib.use("PDF")
import matplotlib.pyplot as plt

if sep == "tab":
    sep = "\t"

r = csv.reader(open(input), delimiter='\t')
mat = np.array([row for row in r], dtype=np.float)

for time_series in mat:
    plt.plot(time_series)

if len(mat[0]) < 5:
    plt.xticks(range(len(mat[0]) + 1), range(len(mat[0]) + 1))

plt.ylabel("Intensity [a.u.]")
plt.xlabel("Time Points")
plt.savefig(output, format=format)
