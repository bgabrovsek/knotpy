"""
Various shared combinatoric functions
"""

from itertools import product, permutations, chain, combinations
from random import random
import os




def elements_from_cycles(cycles):
    """Selects one element from each cycle, cycles are sorted by length
    TODO: why not use itertools.product?
    e.g. [(1,2,3),(4,5)] -> (1,4), (1,5), (2,4),..."""
    # TODO: permute multiple cycles of same length
    sorted_cycles = sorted(cycles, key = lambda c: -len(c))
    return product(*sorted_cycles)


def union(*sets):
    """ returns data union of the arguments """
    #return set.union(*sets) if len(sets) else set() # should be this, but if we start with data list it does not work
    return set.union(*(set(s) for s in sets)) if len(sets) else set()


def get_only_one(l, f):
    """ returns element of list l only if it is the single element with property f, else return None"""
    el = None
    for x in l:
        if f(x):
            if el is None:
                el = x
            else:
                return None

    return el


def choose_with_probability(probs):
    sum_p = sum(probs)
    norm_probs = [1.0*p/sum_p for p in probs ]

#    print(norm_probs)

    r = random()
 #   print(r)
    index = 0
    while(r >= 0 and index < len(norm_probs)):
        r -= norm_probs[index]
       # print(r)
        index += 1
    return index - 1


def min_cyclic_rotation(t, return_index = False):
    """ minimal cyclic rotation of tuple t (canonical form)"""
    min_t = list(t)
    min_shift = 0

    t = list(t)

    for shift in range(1,len(t)):
        t = t[1:] + t[0:1]
        if t < min_t:
            min_t = t
            min_shift = shift

    return min_shift if return_index else min_t



def permute(p, a):

    #print("data",data)
#    print(p,data)
    b = [0]*len(a)
    for pos,x in zip(p,a):
        b[pos] = x

   # print("pair",data,b)
    #print("aa",data)
#    return data
    return a
    return b

def inverse(p):
    """inverse permutation"""
    a = [0]*len(p)
    for i, x in enumerate(p):
        #print((i,x),"data[",x,"] = ",i)
        a[x] = i

    #print(p,"->",data)
    return a

def parted_permutations(h, a = None):
    """ returns parted permutations of data seperated by hash list h
    e.g. h = (1,2,1,1,2) return permutations perm(0,2,3) × perm(1,4)
    parted_permutations([0,0,0,1,1],"abcxy") -> abc-xy, abc-yx, acb-xy, acb-yx, ... , cba-yx
    """
    p = []

    if a is None: a = list(range(len(h)))
    h_set = sorted(set(h))

    position = [] # place parted petmutations in proper positions
    for hash_val in h_set:
        position += [i for i, v in enumerate(h) if v == hash_val]

    for hash_val in h_set:
        p.append(tuple(permutations(a[i] for i, v in enumerate(h) if v == hash_val))) # list of indices with has val

    #final_p = []
    #for q in product(*p):
    #    print(tuple(q0 for q0 in chain(*q)))

    #for q in product(*p):
    #    print(tuple(chain(*q)))

    return [inverse(permute(position,tuple(chain(*q)))) for q in product(*p)]

    #return [tuple(chain(*q)) for q in product(*p)]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def n_chunks(lst, n):
    """yield n chunks of lst."""
    chunk_size = len(lst) // n
    chunk_mod = len(lst) % n
    pos = 0
    for i in range(n):
        end_pos = pos + chunk_size + (1 if chunk_mod else 0)
        if chunk_mod: chunk_mod-=1
        yield lst[pos:end_pos]
        pos = end_pos


#print(list(chunks(list(range(13)),5))) #[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11]]
#print(list(n_chunks(list(range(11)),5))) #[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11]]

def print_export_OLD(filename, s, printQ = False):
   # print("export",filename, s)
    file = open(filename, 'data')
    file.write(str(s)+"\n")
    if printQ: print(s)
    file.close()


def double_combinations_with_repetition(elts, n):
    comb = []
    """ elts select range elements from [(data,x), (b,y), (c,z),...] where we can select n-times, but less than 2 times (update: less than 3 times)
    example: elts = [(data,1), (b,2)], n = 2, should return: ab, bb -> [(data,1),(b,1)], [(b,2)]
    example: elts = A1,B2,C1,D2, should return [(A1,B1,C1),(A1,B1,D1),(A1,B2),(A1,C1,D1),(A1,D2),(B1,C1,D1),(B1,D2),(B2,C2),(B2,D1),(C1,D2)]
    """
    if n == 0: return [[]]
    for i, (e, m) in enumerate(elts):
        # select one element
        for c in double_combinations_with_repetition(elts[i+1:],n-1):
            comb.append([(e,1)] + c)
        # select two elements
        if n >= 2 and m >= 2:
            for c in double_combinations_with_repetition(elts[i + 1:], n - 2):
                comb.append([(e, 2)] + c)
        if n >= 3 and m >= 3:
            for c in double_combinations_with_repetition(elts[i + 1:], n - 3):
                comb.append([(e, 3)] + c)



    return comb

def safe_delete(*filename):
    """
    safe deletes files
    :param filename: files
    """
    for fn in filename:
        if os.path.exists(fn):
            os.remove(fn)
            print("Deleting file", fn+".")


class progress():
    def __init__(self, N, comment):
        self.last_X, self.N, self.count, self.comment = None, N, 0, comment

    def update_progress(self):
        self.count += 1
        X = int(100.0 * self.count / self.N + 0.5)
        if self.last_X != X: print("", end=f"\rn={self.comment}...{X}%   ", flush=True)
        self.last_X = X

    def finish(self):
        print("", end="\r", flush=True)
        print()


class BucketSet():
    """ works as set, but we do not need to compare so"""

    def __init__(self, value = None, number_of_buckets=1021): # use prime number < 1024, for no particular reason
        self.number_of_buckets = number_of_buckets
        self.bucket = [[] for b in range(self.number_of_buckets)] # start empty, elements are "buckets"
        if value is not None:
            self += value

    def __iadd__(self, other):
        #print("add",other)
        if isinstance(other, list) or isinstance(other, BucketSet):
            for elt in other:
                self += elt
        else:
            #print(other, other.hash())
            h = other.hash() % self.number_of_buckets
            if other not in self.bucket[h]:
                self.bucket[h].append(other)
        return self

    def filter(self, condition):
        result = BucketSet()
        for elt in self:
            if condition(elt):
                result += elt
        return result

    def map(self, m):
        result = BucketSet()
        for elt in self:
            result += m(elt)
        return result

    def __iter__(self):
        self.iter_bucket = 0 # current bucket
        self.iter_index = -1 # current position in bucket
        return self

    def __next__(self):
        self.iter_index += 1
        if self.iter_bucket >= self.number_of_buckets: raise StopIteration
        while len(self.bucket[self.iter_bucket]) <= self.iter_index:
                self.iter_bucket += 1
                self.iter_index = 0
                if self.iter_bucket >= self.number_of_buckets: raise StopIteration
        return self.bucket[self.iter_bucket][self.iter_index]

    def __len__(self):
        return sum(len(b) for b in self.bucket)

    def chunks(self, size):
        all_chunks = [[]]
        for x in self:
            if len(all_chunks[-1]) == size: all_chunks.append([])
            all_chunks[-1].append(x)
        return all_chunks




    def sorted(self):
        """ return sorted"""
        self_lst = list(self)
        self_lst.sort()
        return self_lst


def normalize_bucket_names(B, start_int = 0):
    """
    names the elements of the bucket to start_int, start_int+1,...
    :param B: bucket
    :param start_int:
    :return:
    """
    name = start_int
    for knot in B.sorted():
        knot.name = name
        name += 1





def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def arg_replace(s, *repls):
    """
    :param s: string that includes "[1]", "[2]",...
    :param repls: list of arguments
    :return: replaces "[1] with 1st argument, "[2]" with 2nd argument,...
    """
    s_ = s
    for index, r in enumerate(repls):
        s_ = s_.replace("["+str(index+1)+"]", str(r))
    return s_


def merge_dictionaries(*dictionaries):
    d = dict()
    for key in union(*[set(d) for d in dictionaries]):  # loop through all possible keys
        value = None
        for d in dictionaries:
            if value is None and key in d:
                value = d[key]
            elif value is not None and key in d and value != d[key]:
                raise ValueError("Incompatible dictionaries.")
        d[key] = value

    return d
