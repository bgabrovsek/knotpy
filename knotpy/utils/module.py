from copy import deepcopy
import sympy

class module():
    def __init__(self, r=None, s=None):
        if r is not None and s is not None:
            self.terms = [(deepcopy(r), deepcopy(s))]
        else:
            self.terms = []

    def copy(self):
        return deepcopy(self)

    # index, contains
    def index(self, s):
        for i, s_ in enumerate(self.terms):
            if s_[1] == s:
                return i
        return None

    def append(self, r, s=None):
        if s is None:
            r, s = r
        try:
            if (i := self.index(s)) is not None:
                self.terms[i] = (self.terms[i][0] + r, self.terms[i][1])
            else:
                self.terms.append((r, s))  # could append sorted
        except:
            print(self.terms)
            print(i, r, s)
            raise IndexError()
    def extend(self, module_element):
        for rs in module_element:
            self.append(*rs)

    #
    # # for inserting returns the index such that self.terms[i-1] < s < self.terms[i]
    # def __insert_index(self, rs):
    #     # !!!
    #     for index, rs0 in enumerate(self.terms):
    #         if rs0[1] == rs[1]: raise ValueError("Cannot insert existing element.")
    #         if rs0[1] > rs[1]: return index
    #     return len(self.terms) if len(self.terms) else 0  # might as well be just len(self.terms)

    def __contains__(self, s):
        return self.index(s) is not None

    # adding/setting elements

    def __iadd__(self, other):
        if isinstance(other, tuple):
            self.append(*other)
        elif isinstance(other, module):
            self.extend(other)
        else:
            raise ValueError(f"Cannot add type {type(other)} to module instance.")
        return self

    def __isub__(self, other):
        if isinstance(other, tuple):
            self.append(-other[0], other[1])
        elif isinstance(other, module):
            self.extend(-other)
        else:
            raise ValueError(f"Cannot add type {type(other)} to module instance.")
        return self

    def __add__(self, other):
        m = self.copy()
        m += other  # no need of copy
        return m

    def __sub__(self, other):
        m = self.copy()
        m -= other # no need of copy
        return m

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self - other

    def __imul__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only multiplied by coefficients")
        self.terms = [(rs[0] * r, rs[1]) for rs in self.terms]
        return self

    def __mul__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only multiplied by coefficients")
        m = self.copy()
        m *= r
        return m

    def __rmul__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only multiplied by coefficients")
        return self * r

    def __idiv__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only divided by coefficients")
        self.terms = [(rs[0] / r, rs[1]) for rs in self.terms]
        return self

    def __div__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only multiplied by coefficients")
        m = self.copy()
        m /= r
        return m

    def __ifloordiv__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only multiplied by coefficients")
        self.terms = [(rs[0] // r, rs[1]) for rs in self.terms]
        return self

    def __floordiv__(self, r):
        if isinstance(r, module):
            raise ValueError("Module can be only multiplied by coefficients")
        m = self.copy()
        m //= r
        return m

    def __neg__(self):
        m = self.copy()
        m.terms = [(-r, s) for r, s in m.terms]
        return m


    # def iterating

    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index >= len(self.terms):
            raise StopIteration
        self.current_index += 1
        return self.terms[self.current_index-1]

    # search / find / substitute
    # returns r-value of basis element s
    def __getitem__(self, s):
        if (ind := self.index(s)) is None:
            raise ValueError(f"Element {s}not in module.")
        return self.terms[ind][0]

    # returns a list of basis elements true under function filterQ
    def filter(self, filter_function):
        return [s for r, s in self.terms if filter_function(s)]

    # substitution, basis element s replaces with module m
    def __setitem__(self, s, m):
        if (ind := self.index(s)) is None:
            raise ValueError(f"Element {s} not in module.")
        r = self.terms[ind][0]  # get r-value
        del self.terms[ind]
        self.extend(m * r)

    # conversion
    def sort(self):
        self.terms = [(r, s) for r, s in sorted(self.terms, key=lambda pair: pair[1])]

    def to_tuple(self):
        return [(r, s) for r, s in sorted(self.terms, key=lambda pair: pair[1]) if r]

    @staticmethod
    def from_tuples(list_of_tuples):
        expression = module()
        for r, s in list_of_tuples:
            expression.append(r, s)
        return expression

    # comparing
    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        return self.to_tuple() != other.to_tuple()

    def __repr__(self):
        return (" + ".join(str(r)+str(s) for r, s in self.terms)).replace(" + -", " -")

"""
m = module(2, "c") + module(15, "a") - module(3, "x")
print("module:", m)
print("coefficient of 'x':",m['x'])
m['c'] = module(4,'b') + module(-3,'z')
print("substitution:", m)
"""