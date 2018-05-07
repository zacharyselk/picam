#!/usr/bin/python

# Prints the difference between each timestamp and the
#     timestamp before it

import sys

if len(sys.argv) != 2:
    print(len(sys.argv))
    print("Usage Error: %s filename" % sys.argv[0])
    sys.exit

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()
    first_time = 0
    for line in lines:
        print(float(line) - first_time)
        first_time = float(line)
