from numpy import *
import csv
from sys import argv

try:
    input1 = argv[1]
    input2 = argv[2]
    output = argv[3]
except IndexError:
    print "Invalid input!"
    exit(1)

r = csv.reader(open(input1), delimiter='\t')
l = []
for row in r:
    l.append([int(i) for i in row])

centroidsid = array(l[0])
mini = array(l[1])

r = csv.reader(open(input2), delimiter='\t')
mat = array([row for row in r], dtype=float)

centroid_matrix = zeros((mat.shape[0], centroidsid.shape[0]))
for i in range(centroidsid.shape[0]):
    centroid_matrix[:, i] = mat[:, centroidsid[i]-1]

f = open(output,"w")
writer = csv.writer(f, delimiter='\t', lineterminator='\n')

f.write("centroid.matrix\n")
writer.writerows(centroid_matrix)

f.write("\ncentroid.idx\n")
writer.writerow(centroidsid)
f.write("\ngroups\n")

for i in range(mini.shape[0]):
    writer.writerow([i+1, int(mini[i])])
f.close()
