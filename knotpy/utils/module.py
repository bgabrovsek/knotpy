from __future__ import annotations

from copy import deepcopy
from typing import Iterable, Iterator, Hashable, TypeVar, Generic, Union

import sympy as sp

__all__ = ["Module"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

CoefT = TypeVar("CoefT")                 # coefficient type: int, float, sympy.Expr, ...
BasisT = TypeVar("BasisT", bound=Hashable)  # basis label type: str, int, etc.


class Module(Generic[CoefT, BasisT]):
    """Sparse formal linear combination over a basis.

    Stores terms as ``[(coefficient, basis_element), ...]`` and automatically
    combines like basis elements.

    Example:
        >>> m = Module(2, "c") + Module(15, "a") - Module(3, "x")
        >>> m["x"]
        -3
        >>> m["c"]
        2
        >>> m["a"]
        15
        >>> m["c"] = Module(4, "b") + Module(-3, "z")  # substitution
        >>> m.to_tuple()
        [(15, 'a'), (4, 'b'), (-3, 'z'), (-3, 'x')]
    """

    def __init__(self, r: CoefT | None = None, s: BasisT | None = None) -> None:
        """Initialize a module element.

        Args:
            r: Optional coefficient.
            s: Optional basis element. If both `r` and `s` are provided, one term is created.
        """
        if r is not None and s is not None:
            self.terms: list[tuple[CoefT, BasisT]] = [(deepcopy(r), deepcopy(s))]
        else:
            self.terms = []

    def copy(self) -> "Module[CoefT, BasisT]":
        """Return a deep copy."""
        return deepcopy(self)

    # ---- internal/search ----

    def index(self, s: BasisT) -> int | None:
        """Return index of basis element `s` or ``None`` if not present."""
        for i, (_, sb) in enumerate(self.terms):
            if sb == s:
                return i
        return None

    def __contains__(self, s: BasisT) -> bool:  # type: ignore[override]
        """Return True if basis element `s` is present."""
        return self.index(s) is not None

    # ---- mutation/combine ----

    def append(self, r: CoefT | tuple[CoefT, BasisT], s: BasisT | None = None) -> None:
        """Append a term, combining with an existing basis element if present.

        Args:
            r: Coefficient or a (coefficient, basis) pair.
            s: Basis element if `r` is just a coefficient.
        """
        if s is None:
            r, s = r  # type: ignore[misc]
        i = self.index(s)
        if i is not None:
            self.terms[i] = (self.terms[i][0] + r, self.terms[i][1])
        else:
            self.terms.append((r, s))  # could be inserted sorted if desired

    def extend(self, module_element: Iterable[tuple[CoefT, BasisT]]) -> None:
        """Extend by an iterable of (coefficient, basis) pairs."""
        for rs in module_element:
            self.append(*rs)

    # ---- arithmetic ----

    def __iadd__(self, other: "Module[CoefT, BasisT]" | tuple[CoefT, BasisT]) -> "Module[CoefT, BasisT]":
        """In-place addition with another Module or a single (r, s) term."""
        if isinstance(other, tuple):
            self.append(*other)
        elif isinstance(other, Module):
            self.extend(other)
        else:
            raise ValueError(f"Cannot add type {type(other)} to module instance.")
        return self

    def __isub__(self, other: "Module[CoefT, BasisT]" | tuple[CoefT, BasisT]) -> "Module[CoefT, BasisT]":
        """In-place subtraction with another Module or a single (r, s) term."""
        if isinstance(other, tuple):
            self.append(-other[0], other[1])
        elif isinstance(other, Module):
            self.extend((-r, s) for r, s in other.terms)
        else:
            raise ValueError(f"Cannot subtract type {type(other)} from module instance.")
        return self

    def __add__(self, other: "Module[CoefT, BasisT]" | tuple[CoefT, BasisT]) -> "Module[CoefT, BasisT]":
        m = self.copy()
        m += other
        return m

    def __sub__(self, other: "Module[CoefT, BasisT]" | tuple[CoefT, BasisT]) -> "Module[CoefT, BasisT]":
        m = self.copy()
        m -= other
        return m

    def __radd__(self, other) -> "Module[CoefT, BasisT]":
        """Support `sum([...], 0)` pattern."""
        if other == 0:
            return self.copy()
        return self.__add__(other)

    def __rsub__(self, other) -> "Module[CoefT, BasisT]":
        return (-self).__add__(other)

    def __imul__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        """Scalar in-place multiplication."""
        if isinstance(r, Module):
            raise ValueError("Module can only be multiplied by scalars.")
        self.terms = [(coef * r, s) for coef, s in self.terms]
        return self

    def __mul__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        if isinstance(r, Module):
            raise ValueError("Module can only be multiplied by scalars.")
        m = self.copy()
        m *= r
        return m

    def __rmul__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        if isinstance(r, Module):
            raise ValueError("Module can only be multiplied by scalars.")
        return self * r

    def __itruediv__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        """Scalar in-place true division."""
        if isinstance(r, Module):
            raise ValueError("Module can only be divided by scalars.")
        self.terms = [(coef / r, s) for coef, s in self.terms]
        return self

    def __truediv__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        if isinstance(r, Module):
            raise ValueError("Module can only be divided by scalars.")
        m = self.copy()
        m /= r
        return m

    # Backwards-compat: Python 2 names (no-ops in Py3 but keep if old code imports them)
    __idiv__ = __itruediv__      # type: ignore[assignment]
    __div__ = __truediv__        # type: ignore[assignment]

    def __ifloordiv__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        if isinstance(r, Module):
            raise ValueError("Module can only be divided by scalars.")
        self.terms = [(coef // r, s) for coef, s in self.terms]
        return self

    def __floordiv__(self, r: CoefT) -> "Module[CoefT, BasisT]":
        if isinstance(r, Module):
            raise ValueError("Module can only be divided by scalars.")
        m = self.copy()
        m //= r
        return m

    def __neg__(self) -> "Module[CoefT, BasisT]":
        m = self.copy()
        m.terms = [(-r, s) for r, s in m.terms]
        return m

    # ---- iteration / access ----

    def __iter__(self) -> Iterator[tuple[CoefT, BasisT]]:
        """Iterate over terms as ``(coefficient, basis)`` tuples."""
        self._current_index = 0
        return self

    def __next__(self) -> tuple[CoefT, BasisT]:
        if self._current_index >= len(self.terms):
            raise StopIteration
        self._current_index += 1
        return self.terms[self._current_index - 1]

    def __getitem__(self, s: BasisT) -> CoefT:
        """Return the coefficient of basis element `s`.

        Raises:
            KeyError: if `s` is not present.
        """
        ind = self.index(s)
        if ind is None:
            raise KeyError(f"Basis element {s!r} not in module.")
        return self.terms[ind][0]

    def __setitem__(self, s: BasisT, m: "Module[CoefT, BasisT]") -> None:
        """Substitute basis element `s` by a module element `m` (linear expansion)."""
        ind = self.index(s)
        if ind is None:
            raise KeyError(f"Basis element {s!r} not in module.")
        r = self.terms[ind][0]  # current coefficient of s
        del self.terms[ind]
        self.extend((coef * r, sb) for coef, sb in m.terms)

    def filter(self, filter_function) -> list[BasisT]:
        """Return list of basis elements `s` for which `filter_function(s)` is True."""
        return [s for _, s in self.terms if filter_function(s)]

    # ---- conversions / ordering ----

    def sort(self) -> None:
        """Sort terms by basis element (lexicographic)."""
        self.terms = [(r, s) for r, s in sorted(self.terms, key=lambda pair: pair[1])]

    def to_tuple(self) -> list[tuple[CoefT, BasisT]]:
        """Return a sorted, zero-coefficient-pruned term list."""
        return [(r, s) for r, s in sorted(self.terms, key=lambda pair: pair[1]) if r]

    @staticmethod
    def from_tuples(list_of_tuples: Iterable[tuple[CoefT, BasisT]]) -> "Module[CoefT, BasisT]":
        """Construct a Module from an iterable of (coefficient, basis) pairs, combining duplicates."""
        expression: Module[CoefT, BasisT] = Module()
        for r, s in list_of_tuples:
            expression.append(r, s)
        return expression

    # ---- comparison / repr ----

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Module):
            return NotImplemented
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Module):
            return NotImplemented
        return self.to_tuple() != other.to_tuple()

    def __repr__(self) -> str:
        return (" + ".join(f"{r} [{s}]" for r, s in self.terms)).replace(" + -", " -")
