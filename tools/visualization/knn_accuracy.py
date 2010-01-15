from numpy import *
import csv
from sys import argv

try:
    train_set = argv[1]
    train_labels = argv[2]
    test_set = argv[3]
    test_labels = argv[4]
    output = argv[5]
except IndexError:
    print "Invalid input!"
    exit(1)

train_reader = csv.reader(open(train_set), delimiter='\t')
train = [row for row in train_reader]
train_labels_reader = csv.reader(open(train_labels), delimiter='\t')
train_labels = [row for row in train_labels_reader]

test_reader = csv.reader(open(test_set), delimiter='\t')
test = [row for row in test_reader]
test_labels_reader = csv.reader(open(test_labels), delimiter='\t')
test_labels = [row for row in test_labels_reader]

right = 0
wrong = 0

for i, elem in enumerate(test):
    try:
        n = train.index(elem)
    except ValueError:
        pass
    else:
        if train_labels[n] == test_labels[i]:
            right += 1
        else:
            wrong += 1
report = """
kNN accuracy report:

Lenght of the train set:  %d
Lenght of the test set:   %d
Right classifications:    %d
Wrong classifications:    %d
""" % (len(test), right + wrong, right, wrong)

out = open(output, 'w')
out.write(report)
