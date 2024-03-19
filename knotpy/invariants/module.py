"""R-module"""
from copy import deepcopy
from collections import defaultdict
from sympy import *

class Module:

    def __init__(self, r=None, m=None, simplification_function=None):
        # TODO: problem is that modules are not mutable

        self.terms = defaultdict(lambda: Integer(0))
        self.simplification = simplification_function

        if r is None and m is None:
            pass
        elif r is not None and m is not None:
            self.terms[m] = r
        elif r is None and m is not None:
            self.terms[m] = Integer(1)
        else:
            raise ValueError("If the ring element is given, the module element must be also given.")

    def _remove_zero_terms(self):
        """Remove terms of the form 0*m."""
        for m0 in [m for m, r in self.terms.items() if r == 0]:
            del self.terms[m0]

    def filter(self, module_filter: Function):
        new_module = Module()
        raise NotImplemented
        #new_module.terms.update({m: r for m, r in self.terms})


    def __mul__(self, ring_element):
        """
        :param ring_element: element from the ring
        :return:
        """
        for m in self.terms:
            self.terms[m] *= ring_element

        self._remove_zero_terms()

