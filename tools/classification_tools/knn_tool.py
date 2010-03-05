#!/usr/bin/python

from optparse import OptionParser
from knn import knn
import csv

# Command line parsin
parser = OptionParser()
parser.add_option("-t", "--training", metavar = "CSV",
                  dest = "training", help = "training data - required")
parser.add_option("-l", "--labels", metavar = "CSV",
                  dest = "labels", help = "labels file - required")
parser.add_option("-s", "--test-set", metavar = "CSV",
                  dest = "testset", help = "test set data - required")
parser.add_option("-D", "--distance", type = "string", dest = "dist",
                  help = "distance: dtw,ddtw,euclidean,pearson,default=ddtw",
                  default="ddtw")
parser.add_option("-f", "--fast", action = "store_true", default = False,
                  dest = "fast", help = "Fast dtw, default = False")
parser.add_option("-r", "--radius", type = "int",
                  dest = "radius", help = "Accuracy of FastDtw, default=20",
                  default=20)
parser.add_option("-k", "--k", type = "int",
                  dest = "k", help = "k, default = 1", default=1)
parser.add_option("-w", "--weight", action = "store_true", default = True,
                  dest = "weight", help = "Use weighted mode, default = True")
parser.add_option("-o", "--output", metavar = "CSV",
                  dest = "foutp", help = "file output name - required")
parser.add_option("-p", "--processor", type = "str",
                  dest = "pu", help = "Use CPU/GPU, default = CPU",
                  default="CPU")
options, args = parser.parse_args()

if not options.training:
	parser.error("option -t (training data) is required")
if not options.labels:
	parser.error("option -l (labels file) is required")
if not options.testset:
	parser.error("option -s (test set data) is required")
if not options.foutp:
	parser.error("option -o (output) is required")

print "Parameters:"
print "k ",options.k
print "weight",options.weight
print "distance ", options.dist
print "fast", options.fast
print "radius ",options.radius
print "Computing on", options.pu

train_reader = csv.reader(open(options.training), delimiter='\t')
train = [row for row in train_reader]

labels_reader = csv.reader(open(options.labels), delimiter='\t')
labels = [row[0] for row in labels_reader]

ts_reader = csv.reader(open(options.testset), delimiter='\t')
ts = [row for row in ts_reader]

nn = knn.kNN(ts,
             train,
             labels,
             options.weight,
             options.dist,
             options.fast,
             options.radius,
             options.pu)
res = nn.compute(options.k)

w = csv.writer(open(options.foutp, 'w'), delimiter='\t')
for line in res:
    w.writerow([line])
