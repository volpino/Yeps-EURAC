from numpy import *
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
    l.append(row)

centroidsid = array(l[0])
mini = array(l[1])

x, mat, header, title = iodata.load_csv(input2, '\t')

centroid_matrix = zeros((matt.shape[0], centroidsid.shape[0]))
for i in range(centroidsid.shape[0]):
    centroid_matrix[:, i] = matt[:, centroidsid[i]-1]

f=open(output,"w")
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
