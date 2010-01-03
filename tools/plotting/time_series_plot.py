#!/usb/bin/env python

from sys import argv
import iodata

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    sep = argv[1]
    input = argv[2]
    output = argv[3]
except IndexError:
    print "Usage: script <separator> <input> <output>"
    exit(1)
if sep == "tab":
    sep = "\t"

x, mat, header, title = iodata.load_csv(input, sep)

for time_series in mat:
    plt.plot(time_series)

plt.ylabel(title)
#plt.xticks(xrange(len(header)), header, rotation=90)
plt.savefig(output, format="png")
