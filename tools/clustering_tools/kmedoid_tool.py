#!/usr/bin/python

from numpy import *
from optparse import OptionParser
import kmedoid
import iodata
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
parser.add_option("-t", "--tolerance", type = "float",
                  dest = "error", help = "tolerance of algorithm, default = 0.0001", default=0.0001)
parser.add_option("-o", "--output", metavar = "CSV",
                  dest = "foutp", help = "name file output - required")
#parser.add_option("-p", "--plot", type = "str",
#                  dest = "plot", help = "plot clusters (True/False), default = False", default=False)
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
print "data ",options.finp
print "separator ",options.sep
print "cluster ",options.k
print "iteration ",options.nrip
print "distance ",options.met
print "fast", options.fast
print "radius ",options.radius
print "Seed ",options.seed
print "tollerance ",options.error

x, mat, header, title = iodata.load_csv(options.finp, options.sep)
m = kmedoid.Medoid(options.nrip,
                   options.met,
                   options.fast,
                   options.radius,
                   options.seed,
                   options.error)
matt = mat.T
centroidsid, mini = m.compute(options.k, matt)

w = csv.writer(open(options.foutp, 'w'), delimiter='\t')
w.writerow(centroidsid)
w.writerow(mini)


"""
if options.plot == "True":
	import matplotlib
	matplotlib.use("Agg")
	import matplotlib.pyplot as plt
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
	plt.savefig(options.foutp, format="png")
else:
	centroid_matrix = zeros((matt.shape[0], centroidsid.shape[0]))
	for i in range(centroidsid.shape[0]):
		centroid_matrix[:, i] = matt[:, centroidsid[i]-1]

	f=open(options.foutp,"w")
	writer = csv.writer(f, delimiter='\t', lineterminator='\n')

	f.write("Call: iteration %s, distance %s, fast %s, radius %d, seed %s, tollerance %f\n" % (options.nrip,options.met, options.fast,options.radius,options.seed,options.error))
	f.write("centroid.matrix\n")
	writer.writerows(centroid_matrix)

	f.write("\ncentroid.idx\n")
	writer.writerow(centroidsid)
	f.write("\ngroups\n")

	for i in range(mini.shape[0]):
		writer.writerow([i+1, int(mini[i])])
	f.close()
"""
