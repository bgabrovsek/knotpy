import knotpy as kp
from collections import Counter, defaultdict

group_sizes = []
num_crossings = []

for diagrams in kp.load_collection_iterator("data/knotoids-filter-4.txt"):
    group_sizes.append(len(diagrams))
    num_crossings += [len(d)-2 for d in diagrams]
    diagrams = [d for d in diagrams if len(d)-2 <= 6]


print(Counter(group_sizes))
print(Counter(num_crossings))


"""
filter 0
Counter({1: 842, 2: 458, 3: 185, 4: 181, 5: 87, 6: 60, 7: 47, 8: 45, 10: 20, 12: 20, 9: 15, 11: 15, 13: 14, 20: 7, 15: 7, 32: 7, 16: 6, 17: 6, 21: 6, 18: 6, 36: 5, 22: 5, 19: 5, 14: 4, 26: 4, 49: 3, 48: 3, 58: 3, 40: 3, 30: 3, 54: 3, 45: 3, 76: 2, 25: 2, 29: 2, 47: 2, 41: 2, 27: 2, 28: 2, 53: 2, 33: 2, 23: 2, 62: 2, 24: 2, 1043: 1, 87: 1, 227: 1, 225: 1, 373: 1, 1390: 1, 439: 1, 122: 1, 144: 1, 44: 1, 117: 1, 161: 1, 103: 1, 86: 1, 267: 1, 111: 1, 38: 1, 67: 1, 78: 1, 56: 1, 199: 1, 64: 1, 75: 1, 156: 1, 37: 1, 79: 1, 80: 1, 46: 1, 82: 1, 60: 1, 34: 1, 55: 1})
Counter({8: 11489, 7: 2657, 6: 613, 5: 142, 4: 34, 3: 5, 2: 1, 0: 1})

filter 1

Counter({1: 1074, 2: 965, 3: 44, 4: 40, 5: 5, 6: 4, 8: 1, 10: 1})
Counter({8: 2193, 7: 772, 6: 315, 5: 55, 4: 22, 3: 3, 2: 2, 0: 1})


filter 4
Counter({1: 1095, 2: 896, 4: 15, 3: 15, 5: 2})
Counter({8: 2003, 7: 699, 6: 235, 5: 44, 4: 15, 3: 3, 2: 2, 0: 1})

filter 4 flip
Counter({1: 1346, 2: 654, 3: 16, 4: 6, 5: 1})
Counter({8: 1923, 7: 587, 6: 177, 5: 31, 4: 9, 3: 2, 0: 1, 2: 1})


"""