"""
Utilities for manipulating (Laurent) polynomials with SymPy:
- reciprocal transforms f(x) -> f(x^{-1})
- normalization for ordinary and Laurent polynomials
- symmetric normalization under t ↔ 1/t
- canonicalization under permutations of variables
"""

from __future__ import annotations

import re
import itertools as it
from itertools import permutations
from typing import Iterable, Optional, Sequence

import sympy as sp
from typing import Optional, Iterable, Sequence


from sympy import Poly, S
#from sympy import S, Expr, Poly, Symbol, expand, simplify, symbols

__all__ = [
    "reciprocal",
    "normalize_laurent",
    #"normalize_polynomial",
    #"normalize_symmetric",
    "extract_variables",
    #"canonicalize_under_variable_permutation",
]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


def reciprocal(expr: sp.Expr, var) -> sp.Expr:
    """Return the reciprocal transform of a polynomial in a given variable.

    Applies the substitution var → var**(-1) and expands.

    Args:
        expr: SymPy expression.
        var: The variable to invert (Symbol or its name).

    Returns:
        Expr: The transformed expression.
    """
    if isinstance(var, str):
        var = sp.symbols(var)
    return sp.expand(expr.subs(var, var ** (-1)))


def extract_variables(expr: sp.Expr, prefix: Optional[str] = None) -> list[sp.Symbol]:
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

    extracted: list[tuple[str, int, sp.Symbol]] = []
    for sym in all_symbols:
        m = pattern.fullmatch(sym.name)
        if not m:
            continue
        pfx, idx = m.groups()
        if prefix is None or pfx == prefix:
            extracted.append((pfx, int(idx), sym))

    extracted.sort(key=lambda t: (t[0], t[1]))
    return [sym for _, __, sym in extracted]

#
#
# def laurent_to_tuples(expr: sp.Expr | sp.Poly, variables: Optional[Iterable[sp.Symbol] | sp.Symbol] = None):
#     """
#     Return a list of tuples of the form (exponents, coefficient).
#     """
#     expr = expr.as_expr() if isinstance(expr, sp.Poly) else sp.sympify(expr)
#     expr = sp.expand(expr)
#
#     # Early exit for numeric constants
#     if expr.is_number:
#         return [(), expr]
#
#     # Variables
#     if variables is None:
#         vars_seq: Sequence[sp.Symbol] = tuple(sorted(expr.free_symbols, key=str))
#     elif isinstance(variables, sp.Symbol):
#         vars_seq = (variables, )
#     else:
#         vars_seq = tuple(sorted(variables, key=str))
#
#     if not vars_seq:
#         return [(), expr]
#
#     # Split sum into monomials
#     terms = sp.Add.make_args(expr)
#
#     # Gather (coeff, exponent_tuple) allowing fractional exponents
#     tuples: list[tuple[tuple[sp.Rational, ...], sp.Expr]] = []
#     for t in terms:
#         coeff = t.as_coeff_mul()[0]  # numeric coefficient (Integer/Rational/Float)
#         pd = t.as_powers_dict()
#         exps: list[sp.Rational] = []
#         for v in vars_seq:
#             e = pd.get(v, 0)
#             # Coerce to a simplified numeric value if possible
#             e = sp.nsimplify(e)
#             # Require rational (including integer) exponent; allow negatives
#             if not e.is_Rational:
#                 raise ValueError(f"Non-rational exponent {e} for variable {v} in term {t}")
#             exps.append(e)  # keep as Rational
#         tuples.append((tuple(exps), coeff))
#
#     return tuples


from typing import Iterable, Optional, Sequence
import sympy as sp

def laurent_to_tuples(
    expr: sp.Expr | sp.Poly,
    variables: Optional[Iterable[sp.Symbol] | sp.Symbol] = None,
) -> tuple:
    """
    Return a list of (exponents, coefficient) where:
      - exponents is a tuple of Rational exponents (one per variable),
      - coefficient is the remaining factor (may be symbolic),
    assuming all true variables are included in `variables` if given.
    """
    expr = expr.as_expr() if isinstance(expr, sp.Poly) else sp.sympify(expr)
    expr = sp.expand(expr)

    # Establish variable order
    if variables is None:
        vars_seq: Sequence[sp.Symbol] = tuple(sorted(expr.free_symbols, key=str))
    elif isinstance(variables, sp.Symbol):
        vars_seq = (variables,)
    else:
        vars_seq = tuple(sorted(variables, key=str))

    # Numeric constant: zero exponents of appropriate length
    if expr.is_number:
        return [((sp.Integer(0),) * len(vars_seq), expr)], vars_seq

    if not vars_seq:
        # No variables; treat whole expr as a single "constant term"
        return [((), expr)], ()

    terms = sp.Add.make_args(expr)
    result: list[tuple[tuple[sp.Rational, ...], sp.Expr]] = []

    for t in terms:
        pd = t.as_powers_dict()
        exps: list[sp.Rational] = []
        coeff = t
        for v in vars_seq:
            e = pd.get(v, sp.Integer(0))
            # Only simplify when needed
            if not e.is_Rational:
                e = sp.nsimplify(e)
            if not e.is_Rational:
                raise ValueError(f"Non-rational exponent {e} for variable {v} in term {t}")
            exps.append(sp.Rational(e))  # ensure exact Rational
            if e != 0:
                coeff = coeff / (v ** e)
        result.append((tuple(exps), sp.simplify(coeff)))

    return result, vars_seq



def tuples_to_laurent(
    pairs: Iterable[tuple[tuple[sp.Rational, ...], sp.Expr]],
    variables: Iterable[sp.Symbol] | sp.Symbol,
) -> sp.Expr:
    """
    Reconstruct an expanded SymPy expression from (exponents, coefficient) pairs.

    - `pairs`: iterable of (exponents, coefficient), where exponents is a tuple of Rationals.
    - `variables`: the variable order used for the exponent tuples. If a single Symbol is
      provided, it's treated as (that_symbol,). If None, variables are inferred from coefficients
      (useful for constant-only inputs), and exponents must be empty tuples.

    Returns:
      Expanded SymPy expression equivalent to the original Laurent polynomial/series.
    """
    pairs = list(pairs)

    # print("pairs", pairs)
    # print("variables", variables)

    # Establish variable order
    if variables is None:
        # Infer variables only from coefficients; exponents must be empty in this mode
        vars_seq: Sequence[sp.Symbol] = ()
        for exps, coeff in pairs:
            if len(exps) != 0:
                raise ValueError("Cannot infer variables: provide `variables` when exponents are non-empty.")
            if not isinstance(coeff, sp.Basic):
                coeff = sp.sympify(coeff)
    elif isinstance(variables, sp.Symbol):
        vars_seq = (variables,)
    else:
        vars_seq = tuple(variables)

    nvars = len(vars_seq)

    terms: list[sp.Expr] = []
    for exps, coeff in pairs:
        if not isinstance(coeff, sp.Basic):
            coeff = sp.sympify(coeff)

        # Validate exponent vector length
        # print("terms", terms)
        # print("nvars", nvars)
        # print("exps", exps,)
        if nvars == 0:
            if len(exps) != 0:
                raise ValueError("Exponent tuples must be empty when no variables are provided.")
        else:
            if len(exps) != nvars:
                raise ValueError(
                    f"Exponent length {len(exps)} does not match number of variables {nvars}."
                )

        term = coeff
        for v, e in zip(vars_seq, exps):
            # Be strict about rationals to mirror laurent_to_tuples guarantees
            if not sp.Rational(e).is_Rational:
                raise ValueError(f"Non-rational exponent {e} for variable {v}.")
            term *= v ** sp.Rational(e)
        terms.append(term)

    if not terms:
        return sp.Integer(0)

    return sp.expand(sp.Add(*terms))

def normalize_laurent(
        expr: sp.Expr | sp.Poly,
        variables: Optional[Iterable[sp.Symbol] | sp.Symbol] = None,
        allow_variable_sign_change: bool = False,
        allow_variable_permutation: bool = False,
        allow_polynomial_sign_change: bool = False,
    ):

    #print("laurent", expr, variables)

    tuples, variables = laurent_to_tuples(expr, variables)
    vars_seq = tuple(variables)
    n = len(vars_seq)

    # print("_vars_seq", vars_seq)
    # print("tuples", tuples)

    # shift exponents so that all exponents are non-negative
    mins = [min((e[j] for e, _ in tuples), default=0) for j in range(n)]
    if any(mins):
        tuples = [(tuple(e - s for e, s in zip(exps, mins)), coeff) for exps, coeff in tuples]

    if allow_variable_permutation or allow_variable_sign_change or allow_polynomial_sign_change:

        # variable permutations
        perms = list(it.permutations(range(n))) if allow_variable_permutation else [tuple(range(n))]
        signs = list(it.product([-1, 1], repeat=n)) if allow_variable_sign_change else [tuple(1 for _ in range(n))]
        poly_signs = (1, -1) if allow_polynomial_sign_change else (1,)

        best = sorted(tuples, reverse=True)
        best_p = vars_seq

        for p in perms:
            new_tuples = [
                (tuple(exps[p[i]] for i in range(n)), coeff)
                for exps, coeff in tuples
            ]
            for s in signs:
                for poly_s in poly_signs:
                    new_new_tuples = sorted([
                        (exps, poly_s * coeff * sp.prod(sign**power for power, sign in zip(exps, s)))
                        for exps, coeff in new_tuples
                    ], reverse=True)
                    if new_new_tuples > best:
                        best = new_new_tuples
                        best_p = p

        #print(best, best_p)
        tuples = best
        #vars_seq = tuple(vars_seq[best_p[i]] for i in range(n))

    return tuples_to_laurent(tuples, vars_seq)

    #
    # # helpers
    # def sort_tuples(ts):
    #     return sorted(ts, key=lambda t: (t[0], sp.default_sort_key(t[1])))
    #
    # def sign_flip(ts, mask):
    #     if not any(mask): return ts
    #     out = []
    #     for exps, coeff in ts:
    #         flips = sum((m and (int(e) & 1)) for m, e in zip(mask, exps)) & 1
    #         out.append((exps, -coeff if flips else coeff))
    #     return out
    #
    # def permute(ts, perm):
    #     if perm == tuple(range(n)): return ts
    #     return [(tuple(exps[i] for i in perm), coeff) for exps, coeff in ts]
    #
    # # ---- Enumerate candidates ----
    # perms = list(it.permutations(range(n))) if allow_variable_permutation else [tuple(range(n))]
    # masks = list(it.product([0, 1], repeat=n)) if allow_variable_sign_change else [tuple(0 for _ in range(n))]
    #
    # best = sort_tuples(tuples)
    # best_vars = vars_seq
    #
    # for perm in perms:
    #     permuted = permute(tuples, perm)
    #     perm_vars = tuple(vars_seq[i] for i in perm)
    #     for mask in masks:
    #         cand = sort_tuples(sign_flip(permuted, mask))
    #         if cand < best:
    #             best, best_vars = cand, perm_vars



    return tuples_to_laurent(tuples, best_p)


# def normalize_laurent(
#         expr: sp.Expr | sp.Poly,
#         variables: Optional[Iterable[sp.Symbol] | sp.Symbol] = None,
#         allow_variable_sign_change: bool = False,
#         allow_variable_permutation: bool = False,
#     ):
#
#     tuples = laurent_to_tuples(expr, variables)
#
#     # Choose normalization factor
#     if up_to_factor is None:
#         # Shift so each variable's minimal exponent becomes 0
#         mins: list[sp.Rational] = [
#             min(e[i] for _, e in tuples) for i in range(len(vars_seq))
#         ]
#         factor = sp.S.One
#         for v, m in zip(vars_seq, mins):
#             if m != 0:
#                 factor *= v**m
#     else:
#         raise NotImplementedError("Normalization 'up_to_factor' not implemented yet.")
#
#     # Optional sign normalization: make leading term (graded-lex) positive
#     if normalize_sign:
#         # key = (total_degree, then lex) — works with Rationals
#         lead_coeff, _ = max(tuples, key=lambda t: (sum(t[1]), t[1]))
#         if lead_coeff.is_Number and lead_coeff < 0:
#             factor = -factor
#
#     return sp.expand(expr / factor)










#
# def normalize_polynomial(poly, variables=None) -> sp.Poly:
#     """
#     Normalize a (multi)variate polynomial by dividing out the minimal
#     exponent of each variable so all exponents start at 0.
#
#     Accepts either a SymPy Poly or Expr (including constants).
#     If `variables` is given, it fixes variable order; otherwise inferred.
#
#     Returns:
#         sympy.Poly (domain preserved when possible)
#     """
#     # Coerce to Poly
#     if isinstance(poly, sp.Poly):
#         P = poly
#         gens = P.gens
#         dom = P.domain
#     else:
#         expr = sp.sympify(poly)
#
#         # Infer variables if not provided
#         if variables is None:
#             gens = tuple(sorted(expr.free_symbols, key=lambda s: s.name))
#         else:
#             gens = tuple(variables)
#
#         # If there are no variables (constant), create a constant Poly
#         if not gens:
#             # Domain: prefer ZZ if rational, else QQ
#             if expr.is_rational:
#                 return sp.Poly(expr, domain=sp.ZZ) if expr == int(expr) else Poly(expr, domain=sp.QQ)
#             return sp.Poly(expr)
#
#         P = sp.Poly(expr, *gens)
#         dom = P.domain
#
#     # Zero polynomial?
#     monoms = P.monoms()
#     if not monoms:
#         return P
#
#     # Compute minimal exponent per variable
#     min_exps = [min(m[i] for m in monoms) for i in range(len(P.gens))]
#
#     # Build monomial factor
#     factor = sp.S.One
#     for g, e in zip(P.gens, min_exps):
#         if e:
#             factor *= g**e
#
#     # Divide and return as Poly with same generators/domain when possible
#     return sp.Poly(P.as_expr() / factor, *P.gens, domain=dom)

# def normalize_polynomial(poly: Poly) -> Poly:
#     """Normalize a multivariate (non-Laurent) polynomial by removing minimal exponents.
#
#     For each generator, divides the polynomial by the minimal exponent of that
#     generator across all monomials, so exponents start at 0.
#
#     Args:
#         poly: SymPy Poly with nonnegative exponents.
#
#     Returns:
#         Poly: A normalized polynomial with minimal support.
#     """
#     gens = poly.gens
#     monoms = poly.monoms()
#
#     if not monoms:
#         return poly  # zero polynomial
#
#     # Minimal exponent per variable
#     min_exps = [min(m[i] for m in monoms) for i in range(len(gens))]
#
#     # Build monomial factor to divide out
#     factor = S.One
#     for g, e in zip(gens, min_exps):
#         if e:
#             factor *= g ** e
#
#     return Poly(poly.as_expr() / factor, *gens)

#
# def normalize_polynomial(poly, variables=None) -> Poly:
#     """
#     Normalize a (multi)variate polynomial by dividing out the minimal exponent of each
#     variable so all exponents start at 0. Accepts Poly or Expr and always returns Poly.
#
#     If the input is constant and `variables` is not provided (or empty), a dummy generator
#     is used internally so SymPy can construct a Poly.
#     """
#     # Coerce to Poly
#     if isinstance(poly, Poly):
#         P = poly
#         gens = P.gens
#         dom = P.domain
#     else:
#         expr = sp.sympify(poly)
#
#         # Choose generators
#         if variables:
#             gens = tuple(variables)
#         else:
#             # infer from the expression
#             inferred = tuple(sorted(expr.free_symbols, key=lambda s: s.name))
#             if inferred:
#                 gens = inferred
#             else:
#                 # constant: give SymPy a dummy generator so Poly(...) works
#                 gens = (sp.Symbol("_z"),)
#
#         P = Poly(expr, *gens)
#         dom = P.domain
#
#     # Zero polynomial → done
#     if P.is_zero:
#         return P
#
#     # Divide out minimal exponents per generator
#     monoms = P.monoms()
#     min_exps = [min(m[i] for m in monoms) for i in range(len(P.gens))]
#     factor = S.One
#     for g, e in zip(P.gens, min_exps):
#         if e:
#             factor *= g**e
#
#     Q = Poly(P.as_expr() / factor, *P.gens, domain=dom)
#     return Q
#
#
# def normalize_laurent_polynomial(
#     expr: sp.Expr,
#     variables: Optional[Iterable[sp.Symbol]] = None,
#     normalize_sign: bool = True,
# ) -> sp.Expr:
#     """Normalize a (Laurent) polynomial up to monomials and ±1.
#
#     Steps:
#       1) Shift exponents of selected variables so that all are nonnegative.
#       2) Optionally flip overall sign so the leading term has positive coefficient.
#
#     Args:
#         expr: SymPy expression (may have negative exponents).
#         variables: Variables to consider. If None, use all free symbols.
#         normalize_sign: If True, ensure leading term's coefficient is positive.
#
#     Returns:
#         Expr: A canonicalized expression.
#     """
#     expr = sp.expand(expr)
#     variables = list(variables) if variables is not None else sorted(expr.free_symbols, key=str)
#
#     if not variables:
#         return expr
#
#     terms = expr.as_ordered_terms()
#     min_exp = {v: S.Infinity for v in variables}
#
#     for term in terms:
#         for v in variables:
#             _, exp = term.as_coeff_exponent(v)
#             min_exp[v] = min(min_exp[v], exp)
#
#     factor = S.One
#     for v, e in min_exp.items():
#         if e != 0 and e != S.Infinity:
#             factor *= v ** e
#
#     expr = sp.expand(expr / factor)
#
#     if normalize_sign:
#         lead_coeff = expr.as_ordered_terms()[0].as_coeff_Mul()[0]
#         if lead_coeff.could_extract_minus_sign():
#             expr = -expr
#
#     return expr

def normalize_symmetric(expr: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    """Normalize a Laurent polynomial symmetrically in a single variable.

    The result is centered and made symmetric under variable ↔ 1/variable,
    then the overall sign is chosen so the leading term is positive.

    Args:
        expr: SymPy expression.
        variable: The variable to symmetrize.

    Returns:
        Expr: Symmetrically normalized expression.
    """
    #TODO: join this with laurent normalization

    expr = sp.expand(expr)
    terms = expr.as_ordered_terms()

    # Collect exponents for the variable
    powers: list[int] = []
    for term in terms:
        exp = term.as_powers_dict().get(variable, 0)
        powers.append(int(exp))

    if not powers:
        return sp.simplify(expr)

    # Center exponents
    min_exp, max_exp = min(powers), max(powers)
    shift = -(max_exp + min_exp) // 2
    expr_shifted = sp.expand(variable ** shift * expr)

    # Symmetrize
    expr_sym = sp.expand((expr_shifted + expr_shifted.subs(variable, 1 / variable)) / 2)

    # Positive leading coefficient
    leading_term = expr_sym.as_ordered_terms()[0]
    if leading_term.could_extract_minus_sign():
        expr_sym = -expr_sym

    return sp.simplify(expr_sym)





# def canonicalize_under_variable_permutation(
#     expr: sp.Expr,
#     variables: Optional[Sequence[sp.Symbol]] = None,
#     allow_sign_change: bool = False,
# ) -> sp.Expr:
#     """Canonicalize an expression up to permutations of variables (and optionally sign).
#
#     For all permutations of the selected variables, compute the permuted polynomial and
#     choose the lexicographically **minimal** representation of (exponent-vector → coefficient)
#     pairs (optionally also considering the negated polynomial).
#
#     Args:
#         expr: SymPy expression.
#         variables: Sequence of variables to permute. If None, attempts to detect with
#             :func:`extract_variables` and then sorts them.
#         allow_sign_change: If True, also consider -f under permutations and pick the best.
#
#     Returns:
#         Expr: Canonical representative under variable permutations (and ±1 if enabled).
#     """
#     expr = expr.as_expr()
#     expr = sp.expand(expr)
#
#     if variables is None:
#         variables = extract_variables(expr)
#     variables = tuple(sorted(variables, key=str))
#
#     if not variables:
#         return expr
#
#     # Map to dummy variables (s1, s2, ...) to simplify substitution ordering.
#     dummy_vars = sp.symbols(f"s1:{len(variables) + 1}")
#     to_dummy = dict(zip(variables, dummy_vars))
#     expr_dummy = expr.subs(to_dummy)
#
#     best_expr: Optional[sp.Expr] = None
#     best_repr: Optional[tuple] = None
#
#     for perm in permutations(dummy_vars):
#         # Map permuted dummy vars back to the original variable order
#         back_subs = {s: t for s, t in zip(perm, variables)}
#         expr_perm = sp.expand(expr_dummy.subs(back_subs))
#
#         poly = sp.Poly(expr_perm, *variables)
#         rep = tuple(sorted(poly.as_dict().items()))  # canonical monomial representation
#
#         # choose lexicographically minimal (matches docstring)
#         if best_repr is None or rep < best_repr:
#             best_repr = rep
#             best_expr = expr_perm
#
#
#         if allow_sign_change:
#             expr_perm_neg = sp.expand(-expr_perm)
#             poly_neg = sp.Poly(expr_perm_neg, *variables)
#             rep_neg = tuple(sorted(poly_neg.as_dict().items()))
#             if rep_neg > best_repr:
#                 best_repr = rep_neg
#                 best_expr = expr_perm_neg
#
#     # Fallback shouldn't happen, but keep types happy
#     return best_expr if best_expr is not None else expr


if __name__ == "__main__":
    pass
