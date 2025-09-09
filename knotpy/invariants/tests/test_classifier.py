from knotpy import group_by_invariants
from knotpy.tables.tests._helper import _safe_delete_file, _unique

def first_letter(s):
    return s[0]

def last_letter(s):
    return s[-1]

def test_group_by_invariants():
    diagrams = [
        "alpha", "beta", "gamma", "delta",     # common
        "albino", "azzura", "avilda",          # start/end with "a"
        "dilemma", "donetra", "dogma",         # start with "d", end with "a"
        "gummy"                                # outlier
    ]

    inv_funcs_multi = {
        "first": first_letter,
        "last": last_letter
    }

    inv_func_single = first_letter

    expected_keys_multi = {
        (("first", s[0]), ("last", s[-1])) for s in diagrams
    }

    expected_keys_single = {s[0] for s in diagrams}

    # --- Case 1: multi-invariant, parallel=False ---
    groups1 = group_by_invariants(diagrams, inv_funcs_multi, parallel=False)
    actual_keys1 = set(groups1.keys())
    assert actual_keys1 == expected_keys_multi, "Mismatch in multi-func keys (parallel=False)"

    # --- Case 2: multi-invariant, parallel=True ---
    groups2 = group_by_invariants(diagrams, inv_funcs_multi, parallel=True)
    actual_keys2 = set(groups2.keys())
    assert actual_keys2 == expected_keys_multi, "Mismatch in multi-func keys (parallel=True)"

    # --- Case 3: single-invariant, parallel=False ---
    groups3 = group_by_invariants(diagrams, inv_func_single, parallel=False)
    actual_keys3 = set(groups3.keys())
    assert actual_keys3 == expected_keys_single, "Mismatch in single-func keys (parallel=False)"

    # --- Case 4: single-invariant, parallel=True ---
    groups4 = group_by_invariants(diagrams, inv_func_single, parallel=True)
    actual_keys4 = set(groups4.keys())
    assert actual_keys4 == expected_keys_single, "Mismatch in single-func keys (parallel=True)"


def test_saver():
    import knotpy as kp
    codes = ["a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 e0 f3 b2) d=X(g0 g2 e1 b3) e=X(c1 d2 f1 f0) f=X(e3 e2 g1 c2) g=X(d0 f2 d1 h0) h=V(g3)",
     "a=V(b0) b=X(a0 c0 d3 d2) c=X(b1 e3 f3 d0) d=X(c3 f2 b3 b2) e=X(f1 f0 g0 c1) f=X(e1 e0 d1 c2) g=V(e2)",
     "a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 f0) d=X(f3 f2 e1 b2) e=X(g0 d2 f1 c2) f=X(c3 e2 d1 d0) g=V(e0)",
     "a=V(b0) b=V(a0)",
     "a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 f3 g0) e=X(c1 f2 f1 c2) f=X(d1 e2 e1 d2) g=V(d3)",
     "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 d1 b2) d=X(b3 c2 f3 e1) e=X(c1 d3 f1 f0) f=X(e3 e2 g0 d2) g=V(f2)",
     "a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 d1 b0) d=X(b1 c2 e3 f0) e=X(c1 f2 f1 d2) f=X(d3 e2 e1 g0) g=V(f3)",
     "a=V(b3) b=X(c0 d0 d3 a0) c=X(b0 e0 f3 g0) d=X(b1 h0 h3 b2) e=X(c1 h2 f1 f0) f=X(e3 e2 h1 c2) g=V(c3) h=X(d1 f2 e1 d2)", ]

    diagrams = [kp.from_knotpy_notation(_) for _ in codes]
    for i, k in enumerate(diagrams):
        k.name = str(i)

    kp.save_invariants(diagrams, invariant_funcs=kp.affine_index_polynomial, path=_unique + "_invariants.txt", parallel=False)
    _safe_delete_file(_unique + "_invariants.txt")

if __name__ == "__main__":
    test_saver()
    #test_group_by_invariants()