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


# from collections import defaultdict
# from functools import total_ordering
# from numbers import Number
# import operator
#
#
# class Module:
#     """
#     A class representing a formal linear combination of generators with coefficients.
#
#     Each module element is a sum of the form a0*g0 + a1*g1 + ..., where:
#     - ai are coefficients (e.g., integers, floats, sympy expressions, ...)
#     - gi are generators (arbitrary objects that can be compared and hashed)
#
#     The class supports addition, subtraction, scalar multiplication, evaluation,
#     term simplification, indexing, iteration, and comparisons.
#     """
#
#     def __init__(self, terms=None):
#         """
#         Initialize the module with an optional list of (coefficient, generator) terms.
#         """
#         self.terms = defaultdict(lambda: 0)
#         if terms:
#             for coeff, gen in terms:
#                 self.add_term(coeff, gen)
#
#     def add_term(self, coeff, gen):
#         """
#         Add a term coeff * gen to the module, combining with existing term if needed.
#         Removes term if the resulting coefficient is zero.
#         """
#         if coeff == 0:
#             return
#         self.terms[gen] += coeff
#         if self.terms[gen] == 0:
#             del self.terms[gen]
#
#     def __add__(self, other):
#         """Return the sum of two modules."""
#         result = Module(self.to_list())
#         for coeff, gen in other.to_list():
#             result.add_term(coeff, gen)
#         return result
#
#     def __sub__(self, other):
#         """Return the difference of two modules."""
#         return self + (-other)
#
#     def __neg__(self):
#         """Return the negation of the module."""
#         return Module([(-coeff, gen) for gen, coeff in self.terms.items()])
#
#     def __mul__(self, scalar):
#         """Scalar multiplication of the module."""
#         return Module([(coeff * scalar, gen) for gen, coeff in self.terms.items()])
#
#     def __rmul__(self, scalar):
#         """Right scalar multiplication (scalar * module)."""
#         return self * scalar
#
#     def __imul__(self, scalar):
#         """In-place scalar multiplication."""
#         for gen in list(self.terms):
#             self.terms[gen] *= scalar
#             if self.terms[gen] == 0:
#                 del self.terms[gen]
#         return self
#
#     def __truediv__(self, scalar):
#         """Division of the module by a scalar."""
#         return Module([(coeff / scalar, gen) for gen, coeff in self.terms.items()])
#
#     def __floordiv__(self, scalar):
#         """Floor division of the module by a scalar."""
#         return Module([(coeff // scalar, gen) for gen, coeff in self.terms.items()])
#
#     def __contains__(self, gen):
#         """Check if the generator gen appears in the module."""
#         return gen in self.terms
#
#     def __getitem__(self, gen):
#         """Return the coefficient of the generator gen, or 0 if not present."""
#         return self.terms.get(gen, 0)
#
#     def __iter__(self):
#         """Iterate over (generator, coefficient) pairs."""
#         return iter(self.terms.items())
#
#     def to_list(self):
#         """Convert the module to a list of (coefficient, generator) tuples."""
#         return [(coeff, gen) for gen, coeff in self.terms.items()]
#
#     def __eq__(self, other):
#         """Check equality of two modules (same generators and coefficients)."""
#         return dict(self.terms) == dict(other.terms)
#
#     def __ne__(self, other):
#         """Check inequality of two modules."""
#         return not self == other
#
#     def sort(self):
#         """
#         Return the module's terms as a list sorted by generator.
#         Assumes generators are comparable.
#         """
#         return sorted(self.terms.items(), key=lambda x: x[0])
#
#     def evaluate(self, f):
#         """
#         Evaluate the module using a function f applied to generators.
#
#         Returns the sum: a0*f(g0) + a1*f(g1) + ...
#         """
#         return sum(coeff * f(gen) for gen, coeff in self.terms.items())
# #
#
#     def replace(self, gen, replacement_module):
#         """
#         Replace the generator `gen` in the module with another module.
#
#         For example, if m = a*g + ... and we replace g with b0*h0 + b1*h1,
#         the result is a*b0*h0 + a*b1*h1 + ...
#         """
#         if gen not in self.terms:
#             return self  # nothing to replace
#
#         coeff = self.terms.pop(gen)
#         for r_coeff, r_gen in replacement_module:
#             self.add_term(coeff * r_coeff, r_gen)
#         return self

#     def __repr__(self):
#         """Return a string representation of the module."""
#         if not self.terms:
#             return "0"
#         return " + ".join(f"{coeff}*{gen}" for gen, coeff in self.sort())
