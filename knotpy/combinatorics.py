from itertools import product, permutations, chain


def minimal_cyclic_rotation(lst):
    """Returns minimal cyclic rotation of l."""
    return min(lst[i:] + lst[:i] for i in range(len(lst)))
1


#for x in product(permutations([1,2,3]), permutations([6,7])):
#    print(x)




# print(inverse_multi_dict({'a': 0, 'b': 0, 'c': 1}))


def parted_permutations(d):
    """Returns "parted" permutations of keys of d split by values (partition values, classes) of d.
    e.g. d = {'a':0, 'b':0, 'c':0, 'x':1, 'y':1, 'q':2} -> abc-xy-q, abc-yx-q, acb-xy-q, acb-yx-q, ... , cba-yx-q
    """
    d_ = inverse_multi_dict(d)
    for seq_of_seq in product(*[permutations(d_[key]) for key in sorted(d_.keys())]):
        yield list(chain.from_iterable(seq_of_seq))

#for x in parted_permutations({5:0, 6:1, 7:0, 8: 0, 9: 2}): print(x)


