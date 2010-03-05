#!/usr/bin/python

from numpy import *
from optparse import OptionParser
import kmedoid
import csv

# Command line parsin
parser = OptionParser()
parser.add_option("-d", "--data", metavar = "CSV",
                  dest = "finp", help = "data - required")
parser.add_option("-s", "--separator", type = "string",
                  dest = "sep", help = "separator - required")
parser.add_option("-c", "--cluster", type = "int",
                  dest = "k", help = "number of cluster - required")
parser.add_option("-i", "--iteration",  type = "str", dest = "nrip",
                  help = "number of iteration, default=None", default=None)
parser.add_option("-D", "--distance", type = "string",
                  dest = "met", help = "distance: dtw,ddtw,euclidean,pearson,default=ddtw", default="ddtw")
parser.add_option("-f", "--fast", action = "store_true", default = False,
                  dest = "fast", help = "Fast dtw, default = False")
parser.add_option("-r", "--radius", type = "int",
                  dest = "radius", help = "Accuracy of FastDtw, default=20", default=20)
parser.add_option("-S", "--Seed", type = "str",
                  dest = "seed", help = "Seed for function random, default = None", default=None)
parser.add_option("-o", "--output", metavar = "CSV",
                  dest = "foutp", help = "name file output - required")
parser.add_option("-p", "--processor", type = "str",
                  dest = "pu", help = "Use CPU/GPU, default = CPU", default="CPU")
(options, args) = parser.parse_args()

if not options.finp:
	parser.error("option -d (data) is required")
if not options.sep:
	parser.error("option -s (separator) is required")
if options.sep == "tab":
    options.sep = '\t'
if not options.k:
	parser.error("option -c (cluster) is required")
if not options.foutp:
	parser.error("option -o (output) is required")

if options.nrip == 'None':
    options.nrip = None
elif options.nrip:
    try:
        options.nrip = int(options.nrip)
    except ValueError:
        parser.error("option -i: invalid value")

if options.seed == 'None':
    options.seed = None
elif options.seed:
    try:
        options.seed = int(options.seed)
    except ValueError:
        parser.error("option -S: invalid value")

print "Parameters:"
print "separator ",options.sep
print "cluster ",options.k
print "iteration ",options.nrip
print "distance ",options.met
print "fast", options.fast
print "radius ",options.radius
print "Seed ",options.seed
print "Computing on", options.pu

m = kmedoid.Medoid(options.nrip,
                   options.met,
                   options.fast,
                   options.radius,
                   options.seed,
                   pu=options.pu)

r = csv.reader(open(options.finp), delimiter=options.sep)
mat = array([row for row in r], dtype=float)
centroidsid, mini = m.compute(options.k, mat.T)

w = csv.writer(open(options.foutp, 'w'), delimiter='\t')
for elem in centroidsid:
    w.writerow(mat[elem])
w.writerow(mini)
