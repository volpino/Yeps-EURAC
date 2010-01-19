#!/usb/bin/env python

from sys import argv
import iodata

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

x, mat, header, title = iodata.load_csv(input, sep)

for time_series in mat:
    plt.plot(time_series)

if len(mat[0]) < 5:
    plt.xticks(range(len(mat[0])), range(len(mat[0])))

plt.ylabel("Intensity [a.u.]")
plt.xlabel("Time Points")
plt.savefig(output, format=format)
