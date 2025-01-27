#!/usr/bin/python3
import sys

results = {}
for line in sys.stdin:
    c, frequency = line.split('\t', 1)
    results[c] = results.get(c, 0) + int(frequency)
cs = list(results.keys())
for c in cs:
    print(c, results[c])

