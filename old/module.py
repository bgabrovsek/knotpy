from copy import deepcopy
from random import choice

class module():
    """
    Implementation of mathematical left R-module
    """
    def __init__(self, r = None, s = None):
        """
        :param r: coefficient
        :param s: set element
        """
        if r is not None and s is not None:
            self.terms = [(deepcopy(r), deepcopy(s))]
        else:
            self.terms = []

    def copy(self):
        return deepcopy(self)

    # index, contains

    def index(self, s):
        for ind, rs in enumerate(self.terms):
            if rs[1] == s: return ind
        return None

    # for inserting returns the index such that self.terms[i-1] < s < self.terms[i]
    def __insert_index(self, rs):
        for index, rs0 in enumerate(self.terms):
            if rs0[1] == rs[1]: raise ValueError("Cannot insert existing element.")
            if rs0[1] > rs[1]: return index
        return len(self.terms) if len(self.terms) else 0  # might as well be just len(self.terms)

    def __contains__(self, s):
        return self.index(s) is not None

    # adding/setting elements

    def __iadd__(self, other):

        if isinstance(other, tuple):
            index = self.index(other[1])
            if index is None:
                self.terms.insert(self.__insert_index(other), deepcopy(other)) # sorted insert
            else:
              #  print(self.terms[index])
                self.terms[index] = (self.terms[index][0] + other[0], self.terms[index][1]) # no copy!

        elif isinstance(other, module):
            # add two modules, element by element
            for rs in other:
                self += rs # no need of copy

        else: raise ValueError("Cannot iadd this type.")
        return self

    def __add__(self, other):
        m = self.copy()
        m += other # no need of copy
        return m

    def __radd__(self, other): return self + other

    def __isub__(self, other):

        if isinstance(other, tuple):
            index = self.index(other[1])
            if index is None:
                self.terms.insert(self.__insert_index(other), (-deepcopy(other[0]), deepcopy(other[1]))) # sorted insert
            else:
               # print(self.terms[index])
                self.terms[index] = (self.terms[index][0] - other[0], self.terms[index][1]) # no copy!

        elif isinstance(other, module):
            # add two modules, element by element
            for rs in other:
                self -= rs # no need of copy

        else: raise ValueError("Cannot iadd this type.")
        return self

    def __sub__(self, other):
        m = self.copy()
        m -= other # no need of copy
        return m

    def __rsub__(self, other):
        return self - other


    def __imul__(self, r):
        self.terms = [(rs[0] * r, rs[1]) for rs in self.terms]
        return self

    def __mul__(self, r):
        m = self.copy()
        m *= r
        return m

    def __rmul__(self, other): return self * other


    def __idiv__(self, r):
        self.terms = [(rs[0] / r, rs[1]) for rs in self.terms]
        return self

    def __div__(self, r):
        m = self.copy()
        m /= r
        return m

    def __ifloordiv__(self, r):
        self.terms = [(rs[0] // r, rs[1]) for rs in self.terms]
        return self

    def __floordiv__(self, r):
        m = self.copy()
        m //= r
        return m


    # def iterating

    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index >= len(self.terms): raise StopIteration
        self.current_index += 1
        return self.terms[self.current_index-1]


    # search / find / substitute

    # returns r-value of basis element s
    def __getitem__(self, s):
        ind = self.index(s)
        if ind is None: raise  ValueError("Element not in module.")
        return self.terms[ind][0]


    # returns a list of basis elements true under function filterQ
    def filter(self, filterQ):
        return [s for r,s in self.terms if filterQ(s)]

    def choice(self, filterQ = None):
        l = self.filter(filterQ) if filterQ is not None else [s for r,s in self.terms]
        if len(l) == 0: return None # return None if not avail
        return choice(l) # return random elt

    # substitution, basis element s replaces with module m
    def __setitem__(self, s, m):
        ind = self.index(s)
        if ind is None: raise  ValueError("Element not in module.")
        r = self.terms[ind][0] # get r-value
        del self.terms[ind]
        self += m * r # makes a copy of m

    # evaluate basis elements basis by evaluation function
    def eval(self, eval_f):
        if not self.terms:
            return 0
        r, s = self.terms.pop()
        ev = r * eval(s)
        while self.terms:
            r, s = self.terms.pop()
            ev += r * eval(s)
        return ev
    # comparing

    def __eq__(self, other):
        return self.terms == other.terms

    def __ne__(self, other):
        return self.terms != other.terms

    def __repr__(self):
        return (" + ".join( str(r)+str(s) for r, s in self.terms)).replace(" + -", " -")


"""
m = module(2, "c") + module(15, "a") - module(3, "x")  - module(8, "c")
print("module:", m)
print("coefficient of 'x':",m['x'])
m['c'] = module(4,'b') + module(-3,'z')
print("substitution:", m)
"""