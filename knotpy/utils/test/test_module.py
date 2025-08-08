from knotpy.utils.module import Module

import pytest
import sympy as sp

from knotpy.utils.module import Module


def test_construct_and_basic_ops():
    m = Module(2, "c") + Module(15, "a") - Module(3, "x")
    assert m["c"] == 2
    assert m["a"] == 15
    assert m["x"] == -3
    # contains / index
    assert "a" in m and "q" not in m
    # iteration yields terms
    terms = list(m)
    assert all(len(t) == 2 for t in terms)


def test_append_combines_like_terms():
    m = Module()
    m.append(2, "a")
    m.append(3, "a")
    m.append(-5, "a")
    assert "a" in m
    # combined to zero but still stored until pruned via to_tuple()
    assert m["a"] == 0
    assert m.to_tuple() == []  # prunes zeros


def test_add_sub_extend():
    m1 = Module(1, "a") + Module(2, "b")
    m2 = Module(3, "a") - Module(5, "c")
    s = m1 + m2
    assert s.to_tuple() == [(4, "a"), (2, "b"), (-5, "c")]
    d = m1 - m2
    assert d.to_tuple() == [(-2, "a"), (2, "b"), (5, "c")]


def test_scalar_multiply_divide():
    m = Module.from_tuples([(2, "a"), (-3, "b")])
    assert (m * 2).to_tuple() == [(4, "a"), (-6, "b")]
    assert (2 * m).to_tuple() == [(4, "a"), (-6, "b")]

    m2 = m / 2
    # use floats for division check to avoid integer floor surprises
    assert m2.to_tuple() == [(1, "a"), (-3/2, "b")]

    m3 = m // 2
    assert m3.to_tuple() == [(1, "a"), (-2, "b")]  # floor div


def test_radd_sum_zero_seed():
    m1 = Module(1, "a")
    m2 = Module(2, "b")
    total = sum([m1, m2], 0)   # relies on __radd__
    assert total.to_tuple() == [(1, "a"), (2, "b")]


def test_setitem_substitution():
    # m = 2[c] + 15[a] - 3[x]
    m = Module(2, "c") + Module(15, "a") - Module(3, "x")
    # substitute c := 4[b] + (-3)[z]  (i.e., replace basis 'c' by that module)
    m["c"] = Module(4, "b") + Module(-3, "z")
    # should distribute coefficient 2 * ( ... )
    assert set(m.to_tuple()) == {(15, "a"), (8, "b"), (-6, "z"), (-3, "x")}

    # unknown key raises
    with pytest.raises(KeyError):
        _ = m["q"]


def test_filter_and_sort_and_equality():
    m = Module.from_tuples([(3, "c"), (1, "a"), (2, "b")])
    assert m.filter(lambda s: s in {"a", "c"}) == ["c", "a"] or ["a", "c"]

    # sorting only affects internal order, to_tuple returns sorted/pruned
    m.sort()
    assert m.to_tuple() == [(1, "a"), (2, "b"), (3, "c")]

    n = Module.from_tuples([(1, "a"), (2, "b"), (3, "c")])
    assert m == n
    assert not (m != n)


def test_sympy_coefficients():
    x = sp.symbols("x")
    m = Module(x + 1, "u") + Module(2*x, "v")
    # arithmetic w/ sympy Expr
    m2 = 3 * m - Module(x, "u")
    # (3*(x+1) - x) = (2x + 3) for 'u', and 3*(2x) = 6x for 'v'
    u = sp.simplify(m2["u"])
    v = sp.simplify(m2["v"])
    assert u.equals(2*x + 3)
    assert v.equals(6*x)

def test_module():
    m = Module(2, "c") + Module(15, "a") - Module(3, "x")

    assert set(m.to_tuple()) == {(-3, 'x'), (15, 'a'), (2, 'c')}

    m += Module(1, "x")
    assert set(m.to_tuple()) == {(-2, 'x'), (15, 'a'), (2, 'c')}

    m += Module(2, "x")
    assert set(m.to_tuple()) == {(15, 'a'), (2, 'c')}

    m2 = Module(-15, "a") + Module(7, "d")
    m3 = m + m2
    assert set(m3.to_tuple()) == {(2, 'c'), (7, 'd')}

    m3 *= 3
    assert set(m3.to_tuple()) == {(6, 'c'), (21, 'd')}

    assert set((m3 * 2).to_tuple()) == {(12, 'c'), (42, 'd')}
    assert set((m3 * 0).to_tuple()) == set()


# --- manual runner ---
if __name__ == "__main__":
    test_construct_and_basic_ops()
    test_append_combines_like_terms()
    test_add_sub_extend()
    test_scalar_multiply_divide()
    test_radd_sum_zero_seed()
    test_setitem_substitution()
    test_filter_and_sort_and_equality()
    test_sympy_coefficients()
    test_module()
    print("All tests passed.")
