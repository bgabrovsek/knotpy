"""
Read before Theorem 6.

Fig. 7 page 8,
Fig. 15.

Read section 6.

"""

# from draw_tangle import TangleProduct, integral, draw_smooth, draw, crossings
# import matplotlib.pyplot as plt
# from time import time
# import re
# from tqdm import tqdm
# from matplotlib.backends.backend_pdf import PdfPages
# from math import floor

import math


def max_tuple_nesting(t):
    """Recursively finds the maximum depth of nested tuples."""
    if not isinstance(t, tuple):
        return 0  # Base case: Not a tuple, no nesting
    return 1 + max((max_tuple_nesting(sub) for sub in t), default=0)

def smaller(a, b, first=True):
    """ reutrn true if tangle a < b"""
    if a == b:
        return None

    def smt(a, b):
        if isinstance(a, int) and not isinstance(b, int): return True
        if not isinstance(a, int) and isinstance(b, int): return False
        if isinstance(a, int) and isinstance(b, int):
            if a == b: return None
            if a > 0 and b < 0: return True
            return abs(a) > abs(b)

    def depth(t):
        return 0 if not isinstance(t, tuple) else (1 + max((depth(item) for item in t), default=0))

    def flatten(t):
        def flatten_(t):
            if isinstance(t, int):
                yield t
            else:
                for item in t:
                    if isinstance(item, tuple):
                        yield from flatten(item)  # Recursively yield items from nested tuples
                    else:
                        yield item  # Yield non-tuple items as is

        return tuple(flatten_(t))

    def count_int(t):
        return len([x for x in flatten(t) if x])

    def C(t):
        return sum(abs(x) for x in flatten(t))

    sa = str(a)
    sb = str(b)

    cpa = sa.count("(")
    cpb = sb.count("(")
    cca = sa.count(",") - sa.count(",)")
    ccb = sb.count(",")- sb.count(",)")
    cma = sa.count("-")
    cmb = sb.count("-")
    cna = max_tuple_nesting(a)
    cnb = max_tuple_nesting(b)

    if cca < ccb:
        return True
    if cca > ccb:
        return False

    if cpa < cpb:
        return True
    if cpa > cpb:
        return False

    if cna < cnb:
        return True
    if cna > cnb:
        return False

    if cma < cmb:
        return True
    if cma > cmb:
        return False




    la = eval(sa.replace("(","").replace(")",""))
    lb = eval(sb.replace("(","").replace(")",""))

    if la > lb:
        print(la, "  >  ", lb)
        return True
    if la < lb:
        print(lb, "  >  ", la)
        return False

    return sa > sb



    print("Oh no!")
    raise ValueError("oh no")


    if first and C(a) != C(b):
        # print(flatten(a), flatten(b))
        # print(C(a), C(b))
        return C(a) < C(b)

    if first and count_int(a) != count_int(b):
        return count_int(a) < count_int(b)

    if smt(a, b) is not None:
        return smt(a, b)

    """
     2 1 (3 0) -1 < 2 -1 (3 0) -1

     """

    # print(a, b)

    if depth(a) != depth(b):
        return depth(a) < depth(b)

    # if len(a) != len(b):
    #     return len(a) < len(b)

    for aa, bb in zip(a, b):
        # print("recors")
        s = smaller(aa, bb, first=False)
        if s is not None:
            return s
    return None


def custom_sort(items):
    for i in range(1, len(items)):
        key_item = items[i]
        j = i - 1
        # Compare using the `smaller` function
        while j >= 0 and smaller(key_item, items[j]):
            items[j + 1] = items[j]
            j -= 1
        # Place the key_item at the correct position
        items[j + 1] = key_item
    return items



def sort_list(lst):
    """Sorts a list using the provided comparator function `smaller(a, b)`."""
    sorted_lst = lst[:]  # Make a copy to avoid modifying the original list

    print("Sorting:", lst)

    # Insertion sort algorithm
    for i in range(1, len(sorted_lst)):
        key = sorted_lst[i]
        j = i - 1
        while j >= 0 and not smaller(sorted_lst[j], key):  # If sorted_lst[j] > key
            sorted_lst[j + 1] = sorted_lst[j]
            j -= 1
        sorted_lst[j + 1] = key

    return sorted_lst

#
# def compute_tuple_properties(t):
#     """
#     Computes the properties of a nested tuple for sorting purposes:
#     1. Minimal sum of absolute values of all integers inside all nests.
#     2. Least nested depth.
#     3. Shortest tuple length.
#     4. Largest numbers for tie-breaking (compared lexicographically).
#     5. Priority to positive numbers over negatives.
#
#     Parameters:
#     - t (tuple): A nested tuple of integers.
#
#     Returns:
#     - tuple: A tuple of sorting keys based on the defined priorities.
#     """
#
#     def flatten_and_depth(nested, current_depth=0):
#         """Flatten the nested tuple and compute the depth."""
#         max_depth = current_depth
#         elements = []
#         for item in nested:
#             if isinstance(item, tuple):
#                 sub_elements, sub_depth = flatten_and_depth(item, current_depth + 1)
#                 elements.extend(sub_elements)
#                 max_depth = max(max_depth, sub_depth)
#             else:
#                 elements.append(item)
#         return elements, max_depth
#
#     # Flatten the tuple and calculate its depth
#     flattened, depth = flatten_and_depth(t)
#
#     # 1. Sum of absolute values of all integers
#     abs_sum = sum(abs(x) for x in flattened)
#
#     # 2. Depth of the tuple (least depth has priority)
#     # The `depth` is already computed during flattening.
#
#     # 3. Shortest tuple length
#     total_length = len(flattened)
#
#     # 4. Largest numbers for tie-breaking (compared lexicographically)
#     largest_numbers = sorted(flattened, reverse=True)
#
#     # 5. Positive numbers priority for tie-breaking
#     positives_priority = [-1 if x < 0 else 0 for x in flattened]
#
#     return (abs_sum, depth, total_length, largest_numbers, positives_priority)
#

# def sort_nested_tuples(nested_tuples):
#     """
#     Sorts a list of nested tuples based on the defined priorities.
#
#     Parameters:
#     - nested_tuples (list of tuple): The list of tuples to be sorted.
#
#     Returns:
#     - list of tuple: The sorted list of tuples.
#     """
#     return sorted(nested_tuples, key=lambda x: compute_tuple_properties(x[0]))
#





if __name__ == "__main__":



    tangles = []
    names = []
    best_cols = [] # minimal/positive representative of a tangle

    with open("up_to_10_extra_sorted.txt", "wt") as g:
        with open("up_to_10_extra.txt") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(" ")
                same = eval(line[-1])
                rep = [col[1] if col[1] != "-" else col[0] for col in same]
                rep = [eval("(" + x + ",)") for x in rep]
                # print(rep)
                # print(sort_list(list(rep)))
                # exit()
                best_rep = sort_list(list(rep))[0]
                index = rep.index(best_rep)
                print(index, str(best_rep).replace(" ","")[1:-1])
                g.write(f"{index} {str(best_rep).replace(' ','')[1:-1]}\n")

    exit()

    items = [
        '-2,(-2,0),(3,1,0),1,1',
        '3,1,(-2,(-2,0),0),1,1',
        '3,1,(-2,(-2,0),0),1,1,0',
        '-3,-1,(2,(2,0),0),-1,-1,0',
        '-2,(-2,0),(3,1,0),1,1,0',
        '2,(2,0),(-3,-1,0),-1,-1,0',
        '2,(2,0),(-3,-1,0),-1,-1',
        '-3,-1,(2,(2,0),0),-1,-1',
    ]

    # items = [
    #     "(-2, (-2, 0), (3, 1, 0), 1, 1)",
    #     "(3, 1, (-2, (-2, 0), 0), 1, 1)"
    # ]
    tups = [eval("("+m+")") for m in items]

    print(smaller(tups[0], tups[1]))
    print(smaller(tups[1], tups[0]))

    s = sort_list(tups)
    for x in s:
        print(x)
        #
        # for i, line in enumerate(lines):
        #     line = eval(line.strip())
        #     line = [list(col) for col in line]
        #
        #     for col in line:
        #         if col[1] == "-":
        #             col[1] = col[0]
        #         print(col)
        #     conway = [eval("(" + col[1] + ",)") for col in line]
        #
        #     exit()
        #

        # representative = line[0]

# ! [('4,1,(5,-1)', '-5,(5,0)', "('e','x','μz','μy')"), ('4,1,(5,-1),0', '-5,(5,0),0', "('ηx','μηy','μηz','η')"), ('5,(4,1,-1),0', '5,(-5,0),0', "('μηx','ηy','ηz','μη')"), ('5,(4,1,-1)', '5,(-5,0)', "('y','z','μ','μx')")]