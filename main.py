#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main tests for PlanarDiagram class...
"""
from itertools import combinations, chain, product

import itertools

def nested_partitions(n):
    # Nested partitions of integers, with non-leading 0's
    yield (n,)
    yield (n,0)
    for i in range(1, n):  # split "n" to "(i) + (n-i)"
        for q in nested_partitions(i):  # partitions of i
            for p in nested_partitions(n-i):  # partitions of (n-i)
                yield q + p  # flatten both
                if len(q) > 1:
                    yield (q,) + p  # flatten only left side
                    yield (q, 0) + p
                if len(p) > 1:
                    yield q + (p,)  # flatten only right side
                    yield q + (p, 0)
                if len(p) > 1 and len(q) > 1:
                    yield (q,) + (p,)  # flatten neither
                    yield (q, 0) + (p, 0)


n = 0
for x in nested_partitions(10):
    n += 1
    if n % 1000000 == 0:
        print(x)
    pass

exit()

print("All of them:")
for x in nested_partitions(3):
    print(x)

print("Unique ones:")
used = set()
for x in nested_partitions(3):
    if x not in used:
        print(x)
        used.add(x)

p = nested_partitions(3)
print("all", len(p), "unique", len(set(p)))

exit()

def flatten(a):
    return [c for b in a for c in b]

def seq(n):
    print(n)
    if n <= 1:
        yield [n]
    else:
        yield [n]
        for i in range(1,n+1):
            for p in product(seq(i), seq(n-i)):
                yield p
for x in seq(2):
    print(x)
"""
((5, 6, 7, 8),)
((5,), (6, 7, 8))
((5, 6), (7, 8))
((5, 6, 7), (8,))
((5,), (6,), (7, 8))
((5,), (6, 7), (8,))
((5, 6), (7,), (8,))
((5,), (6,), (7,), (8,))
"""

#

# for c in chain(*(combinations(range(1, len(a)),r) for r in range(len(a))))):
#     print()
#     for i, j in zip((0,) + c, c + (len(a)+1,)):
#         print(a[i:j], end="+")
