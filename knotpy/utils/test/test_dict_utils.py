# tests/test_dict_utils.py

import math
import pytest

from knotpy.utils.dict_utils import (
    compare_dicts,
    invert_dict,
    invert_multi_dict,
    invert_dict_of_sets,
    invert_nested_dict,
    LazyDict,
    IdentityDict,
    ClassifierDict,
    common_dict,
)

# --- compare_dicts -----------------------------------------------------------

def test_compare_dicts_equal_simple():
    a = {"x": 1, "y": 2}
    b = {"x": 1, "y": 2}
    assert compare_dicts(a, b) == 0

def test_compare_dicts_ordering_by_keys():
    a = {"a": 1}
    b = {"b": 1}
    assert compare_dicts(a, b) == -1
    assert compare_dicts(b, a) == 1

def test_compare_dicts_exclude_and_include():
    a = {"a": 1, "b": 2, "_tmp": 999}
    b = {"a": 1, "b": 3, "_tmp": 111}
    assert compare_dicts(a, b, include_only_keys=["a"]) == 0
    assert compare_dicts(a, b, include_only_keys=["b"]) == -1

def test_compare_dicts_nested():
    a = {"meta": {"u": 1, "v": 2}, "z": 0}
    b = {"meta": {"u": 1, "v": 3}, "z": 0}
    assert compare_dicts(a, b) == -1

def test_compare_dicts_sets():
    a = {"s": {3, 1, 2}}
    b = {"s": {1, 2, 3}}
    assert compare_dicts(a, b) == 0

def test_compare_dicts_type_mismatch():
    a = {"x": 1}
    b = {"x": "1"}
    with pytest.raises(TypeError):
        compare_dicts(a, b)

# --- invert_* ---------------------------------------------------------------

def test_invert_dict_unique_values():
    d = {"a": 1, "b": 2}
    inv = invert_dict(d)
    assert inv == {1: "a", 2: "b"}

def test_invert_dict_duplicate_value_raises():
    d = {"a": 1, "b": 1}
    with pytest.raises(ValueError):
        invert_dict(d)

def test_invert_multi_dict_groups():
    d = {"a": 1, "b": 2, "c": 1}
    inv = invert_multi_dict(d)
    assert inv == {1: {"a", "c"}, 2: {"b"}}

def test_invert_dict_of_sets():
    d = {"x": {1, 2}, "y": {2, 3}}
    inv = invert_dict_of_sets(d)
    assert inv == {1: {"x"}, 2: {"x", "y"}, 3: {"y"}}

def test_invert_nested_dict():
    d = {
        "A": {"p": 1, "q": 2},
        "B": {"p": 1, "q": 2},
        "C": {"p": 1, "q": 9},
    }
    inv = invert_nested_dict(d)
    assert inv[(1, 2)] == {"A", "B"}
    assert inv[(1, 9)] == {"C"}

# --- IdentityDict -----------------------------------------------------------

def test_identity_dict_missing_returns_key():
    d = IdentityDict()
    assert d["alpha"] == "alpha"
    assert d["alpha"] == "alpha"

# --- LazyDict ---------------------------------------------------------------

def test_lazydict_loads_on_access_and_evaluates_once():
    calls = {"load": 0, "eval": 0}

    def load():
        calls["load"] += 1
        return {"a": "2 + 2", "b": "40 + 2"}

    def evaluate(expr: str) -> int:
        calls["eval"] += 1
        return eval(expr)

    d = LazyDict(load, evaluate)
    assert calls["load"] == 0
    assert d["a"] == 4
    assert calls["load"] == 1
    assert calls["eval"] == 1
    assert d["a"] == 4
    assert calls["eval"] == 1
    assert d["b"] == 42
    assert calls["eval"] == 2

def test_lazydict_reload():
    def load():
        return {"x": "10"}

    def evaluate(expr: str) -> int:
        return int(expr)

    d = LazyDict(load, evaluate)
    assert d["x"] == 10
    d["x"] = 99
    assert d["x"] == 99
    d.reload()
    assert d["x"] == 10

# --- ClassifierDict ---------------------------------------------------------

def test_classifier_dict_groups_by_functions():
    funcs = {
        "parity": lambda x: x % 2,
        "sign": lambda x: (x > 0) - (x < 0),
    }
    cd = ClassifierDict(funcs)
    for v in [1, 2, -3, -4, 0]:
        cd.append(v)

    assert sorted(cd.keys()) == sorted({
        (1, 1), (0, 1), (1, -1), (0, -1), (0, 0)
    })
    assert 1 in cd[(1, 1)]
    assert -3 in cd[(1, -1)]
    assert 0 in cd[(0, 0)]

# --- common_dict ------------------------------------------------------------

def test_common_dict_intersection():
    a = {"x": 1, "y": 2}
    b = {"x": 1, "y": 999, "z": 0}
    c = {"x": 1}
    assert common_dict(a, b, c) == {"x": 1}

def test_common_dict_empty_input():
    assert common_dict() == {}

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Manual run: call all test functions directly
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            print(f"Running {name}...")
            func()
    print("All manual tests passed.")
