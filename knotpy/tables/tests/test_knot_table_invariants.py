from knotpy import LazyDict
from knotpy.tables.invariant_writer import InvariantTableWriter, save_invariant_table
from knotpy.tables.invariant_reader import load_invariant_table, _evaluate_dictionary
from knotpy.notation.native import from_knotpy_notation, to_knotpy_notation
from knotpy.notation.em import from_condensed_em_notation
from sympy import sympify
from functools import partial

from knotpy.tables.tests._helper import _safe_delete_file, _unique

def helper_test_save_diagram_table():
    table = {
        "3_1": {
            "diagram": from_condensed_em_notation("b1c0c3b2,c1a0a3c2,a1b0b3a2"),
            "alexander": sympify("t**2 - t + 1"),
            "jones": sympify("-t**4 + t**3 + t"),
            "conway": sympify("z**2 + 1"),
            "unknotting": int("1"),
            "symmetry": "reversible",
            "symmetry_group": "Z2"
        },
        "4_1": {
            "diagram": from_condensed_em_notation("c3d0b3b2,d3c0a3a2,b1d2d1a0,a1c2c1b0"),
            "alexander": sympify("t**2 - 3*t + 1"),
            "jones": sympify("t**2 - t + 1 - 1/t + t**(-2)"),
            "conway": sympify("a**2*z**2 - a**2 + a*z**3 - a*z + 2*z**2 - 1 + z**3/a - z/a + z**2/a**2 - 1/a**2"),
            "unknotting": int("1"),
            "symmetry": "fully amphicheiral",
            "symmetry_group": "D4"
        },
        "5_1": {
            "diagram": from_condensed_em_notation("c1d0d3c2,d1e0e3d2,e1a0a3e2,a1b0b3a2,b1c0c3b2"),
            "alexander": sympify("t**4 - t**3 + t**2 - t + 1"),
            "jones": sympify("-t**7 + t**6 - t**5 + t**4 + t**2"),
            "conway": sympify(
                "z**4/a**4 - 4*z**2/a**4 + 3/a**4 + z**3/a**5 - 2*z/a**5 + z**4/a**6 - 3*z**2/a**6 + 2/a**6 + z**3/a**7 - z/a**7 + z**2/a**8 + z/a**9"),
            "unknotting": int("2"),
            "symmetry": "reversible",
            "symmetry_group": "Z2"
        }
    }

    #print("TABLE", table)
    for name, d in table.items():
        d["diagram"].name = name

    table_keys_are_diagrams = {
        v["diagram"]: {_: v[_] for _ in ["alexander", "jones", "conway", "symmetry", "symmetry_group", "unknotting"]}
        for v in table.values()
    }

    #print("DIAG", table_keys_are_diagrams)

    save_invariant_table(
        filename=_unique + "_knot_table.csv",
        table=table,
        comment="This is a comment")

    save_invariant_table(
        filename=_unique + "_knot_table2.csv",
        table=table_keys_are_diagrams,
        comment="This is a comment")
    # t = InvariantTableWriter("test_knot_table.csv",["jones", "alexander"])
    #
    # t.close()

def helper_load_diagram_table():
    table1 = load_invariant_table(_unique + "_knot_table.csv")
    table2 = load_invariant_table(_unique + "_knot_table2.csv")


    # TODO: missing asserts

    return table1, table2


def helper_lazy_load_diagram_table():

    lazy1 = LazyDict(load_function=partial(load_invariant_table, filename="test_knot_table.csv", lazy=True),
                     eval_function=_evaluate_dictionary)

    lazy2 = LazyDict(load_function=partial(load_invariant_table, filename="test_knot_table2.csv", lazy=True),
                     eval_function=_evaluate_dictionary)


    # print("Table 1")
    # for key, value in lazy1.items():
    #     print(key, ":", value)
    #
    # print()
    # print("Table 2")
    # for key, value in lazy2.items():
    #     print(key, ":", value)

    return lazy1, lazy2


def test_compare_lazy_non_lazy():
    helper_test_save_diagram_table()
    t1, t2 = helper_load_diagram_table()
    l1, l2 = helper_lazy_load_diagram_table()

    # print(type(t1), type(t2))
    # print(type(l1), type(l2))

    # assert t1 == l1
    # assert t2 == l2

    _safe_delete_file(_unique + "_knot_table.csv")
    _safe_delete_file(_unique + "_knot_table2.csv")

    # TODO: missing all

if __name__ == "__main__":
    #test_save_diagram_table()
    #test_load_diagram_table()
    #test_lazy_load_diagram_table()
    test_compare_lazy_non_lazy()