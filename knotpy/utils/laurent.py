"""
Utilities for manipulating (Laurent) polynomials with SymPy:
- reciprocal transforms f(x) -> f(x^{-1})
- normalization for ordinary and Laurent polynomials
- symmetric normalization under t ↔ 1/t
- canonicalization under permutations of variables
"""

from __future__ import annotations

import re
from itertools import permutations
from typing import Iterable, Optional, Sequence

from sympy import S, Expr, Poly, Symbol, expand, simplify, symbols

__all__ = [
    "reciprocal",
    "normalize_polynomial",
    "normalize_laurent_polynomial",
    "normalize_symmetric",
    "extract_variables",
    "canonicalize_under_variable_permutation",
]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


def reciprocal(expr: Expr, var: Symbol | str) -> Expr:
    """Return the reciprocal transform of a polynomial in a given variable.

    Applies the substitution var → var**(-1) and expands.

    Args:
        expr: SymPy expression.
        var: The variable to invert (Symbol or its name).

    Returns:
        Expr: The transformed expression.
    """
    if isinstance(var, str):
        var = symbols(var)
    return expand(expr.subs(var, var ** (-1)))


def normalize_polynomial(poly: Poly) -> Poly:
    """Normalize a multivariate (non-Laurent) polynomial by removing minimal exponents.

    For each generator, divides the polynomial by the minimal exponent of that
    generator across all monomials, so exponents start at 0.

    Args:
        poly: SymPy Poly with nonnegative exponents.

    Returns:
        Poly: A normalized polynomial with minimal support.
    """
    gens = poly.gens
    monoms = poly.monoms()

    if not monoms:
        return poly  # zero polynomial

    # Minimal exponent per variable
    min_exps = [min(m[i] for m in monoms) for i in range(len(gens))]

    # Build monomial factor to divide out
    factor = S.One
    for g, e in zip(gens, min_exps):
        if e:
            factor *= g ** e

    return Poly(poly.as_expr() / factor, *gens)


def normalize_laurent_polynomial(
    expr: Expr,
    variables: Optional[Iterable[Symbol]] = None,
    normalize_sign: bool = True,
) -> Expr:
    """Normalize a (Laurent) polynomial up to monomials and ±1.

    Steps:
      1) Shift exponents of selected variables so that all are nonnegative.
      2) Optionally flip overall sign so the leading term has positive coefficient.

    Args:
        expr: SymPy expression (may have negative exponents).
        variables: Variables to consider. If None, use all free symbols.
        normalize_sign: If True, ensure leading term's coefficient is positive.

    Returns:
        Expr: A canonicalized expression.
    """
    expr = expand(expr)
    variables = list(variables) if variables is not None else sorted(expr.free_symbols, key=str)

    if not variables:
        return expr

    terms = expr.as_ordered_terms()
    min_exp: dict[Symbol, Expr] = {v: S.Infinity for v in variables}

    for term in terms:
        for v in variables:
            _, exp = term.as_coeff_exponent(v)
            min_exp[v] = min(min_exp[v], exp)

    factor = S.One
    for v, e in min_exp.items():
        if e != 0 and e != S.Infinity:
            factor *= v ** e

    expr = expand(expr / factor)

    if normalize_sign:
        lead_coeff = expr.as_ordered_terms()[0].as_coeff_Mul()[0]
        if lead_coeff.could_extract_minus_sign():
            expr = -expr

    return expr


def normalize_symmetric(expr: Expr, variable: Symbol) -> Expr:
    """Normalize a Laurent polynomial symmetrically in a single variable.

    The result is centered and made symmetric under variable ↔ 1/variable,
    then the overall sign is chosen so the leading term is positive.

    Args:
        expr: SymPy expression.
        variable: The variable to symmetrize.

    Returns:
        Expr: Symmetrically normalized expression.
    """
    expr = expand(expr)
    terms = expr.as_ordered_terms()

    # Collect exponents for the variable
    powers: list[int] = []
    for term in terms:
        exp = term.as_powers_dict().get(variable, 0)
        powers.append(int(exp))

    if not powers:
        return simplify(expr)

    # Center exponents
    min_exp, max_exp = min(powers), max(powers)
    shift = -(max_exp + min_exp) // 2
    expr_shifted = expand(variable ** shift * expr)

    # Symmetrize
    expr_sym = expand((expr_shifted + expr_shifted.subs(variable, 1 / variable)) / 2)

    # Positive leading coefficient
    leading_term = expr_sym.as_ordered_terms()[0]
    if leading_term.could_extract_minus_sign():
        expr_sym = -expr_sym

    return simplify(expr_sym)


def extract_variables(expr: Expr, prefix: Optional[str] = None) -> list[Symbol]:
    """Extract variables of the form <prefix><digits> from a SymPy expression.

    Examples:
        - prefix=None  → returns all symbols like t1, x2, a10, grouped by (prefix, index)
        - prefix="t"   → returns only t1, t2, ...

    Args:
        expr: SymPy expression.
        prefix: Optional prefix filter.

    Returns:
        list[Symbol]: Symbols sorted by (prefix, numeric index).
    """
    all_symbols = expr.free_symbols
    pattern = re.compile(r"^([A-Za-z_]+)(\d+)$")

    extracted: list[tuple[str, int, Symbol]] = []
    for sym in all_symbols:
        m = pattern.fullmatch(sym.name)
        if not m:
            continue
        pfx, idx = m.groups()
        if prefix is None or pfx == prefix:
            extracted.append((pfx, int(idx), sym))

    extracted.sort(key=lambda t: (t[0], t[1]))
    return [sym for _, __, sym in extracted]


def canonicalize_under_variable_permutation(
    expr: Expr,
    variables: Optional[Sequence[Symbol]] = None,
    allow_sign_change: bool = False,
) -> Expr:
    """Canonicalize an expression up to permutations of variables (and optionally sign).

    For all permutations of the selected variables, compute the permuted polynomial and
    choose the lexicographically **minimal** representation of (exponent-vector → coefficient)
    pairs (optionally also considering the negated polynomial).

    Args:
        expr: SymPy expression.
        variables: Sequence of variables to permute. If None, attempts to detect with
            :func:`extract_variables` and then sorts them.
        allow_sign_change: If True, also consider -f under permutations and pick the best.

    Returns:
        Expr: Canonical representative under variable permutations (and ±1 if enabled).
    """
    expr = expand(expr)

    if variables is None:
        variables = extract_variables(expr)
    variables = tuple(sorted(variables, key=str))

    if not variables:
        return expr

    # Map to dummy variables (s1, s2, ...) to simplify substitution ordering.
    dummy_vars = symbols(f"s1:{len(variables) + 1}")
    to_dummy = dict(zip(variables, dummy_vars))
    expr_dummy = expr.subs(to_dummy)

    best_expr: Optional[Expr] = None
    best_repr: Optional[tuple] = None

    for perm in permutations(dummy_vars):
        # Map permuted dummy vars back to the original variable order
        back_subs = {s: t for s, t in zip(perm, variables)}
        expr_perm = expand(expr_dummy.subs(back_subs))

        poly = Poly(expr_perm, *variables)
        rep = tuple(sorted(poly.as_dict().items()))  # canonical monomial representation

        # choose lexicographically minimal (matches docstring)
        if best_repr is None or rep < best_repr:
            best_repr = rep
            best_expr = expr_perm

        if allow_sign_change:
            expr_perm_neg = expand(-expr_perm)
            poly_neg = Poly(expr_perm_neg, *variables)
            rep_neg = tuple(sorted(poly_neg.as_dict().items()))
            if rep_neg < best_repr:
                best_repr = rep_neg
                best_expr = expr_perm_neg

    # Fallback shouldn't happen, but keep types happy
    return best_expr if best_expr is not None else expr


if __name__ == "__main__":
    pass
