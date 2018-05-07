#!/usr/bin/python3

import sys

with open(sys.argv[-1], 'r') as f:
    lines = f.readlines()
    total = 0
    prev_time = 0;

    for line in lines:
        total += float(line) - prev_time
        prev_time = float(line)
    mean = total / len(lines)

    deviation_sum = 0
    prev_time = 0
    
    for line in lines:
        deviation_sum += (float(line)-prev_time-mean)**2
        prev_time = float(line)
    standard_deviation = deviation_sum / len(lines)

    
    units = 'ms'
    if standard_deviation < 1:
        units = '\xB5s'
        standard_deviation *= 1000.0
    elif standard_deviation >= 1000:
        units = 'sec'
        standard_deviation /= 1000.0
        
    print('Standard Deviation: %f %s' % (standard_deviation, units))
