from knotpy.utils.dict_utils import LazyDict#, #LazyEvalDict, LazyLoadDict

_loaded = False
_evaluated = []

def _data_loader():
    global _loaded
    _loaded = True
    return {"a": "100-99", "b": "100-98", "c": "100-97", "d": "100-96"}

def _eval(s: str):
    global _evaluated
    #print("[evaluating {}]".format(s))
    _evaluated.append(s)
    return eval(s)

def test_lazy_load():
    global _loaded

    _loaded = False
    d = LazyDict(_data_loader)
    assert not _loaded
    value = d["a"]
    assert _loaded
    assert value == "100-99"


    _loaded = False
    d = LazyDict(_data_loader)
    assert not _loaded
    value = "a" in d
    assert _loaded
    assert value

def test_lazy_eval():
    global _evaluated
    _evaluated = []

    d = LazyDict(_data_loader, _eval)
    assert _evaluated == []
    v = d["a"]
    assert _evaluated == ["100-99"]
    assert v == 1
    v = d["b"]
    assert _evaluated == ["100-99", "100-98"]
    assert v == 2

    v = d["b"]
    assert _evaluated == ["100-99", "100-98"]
    assert v == 2

def test_lazy_load_eval():
    global _loaded, _evaluated
    _evaluated = []
    _loaded = False
    d = LazyDict(_data_loader, _eval)
    assert not _loaded
    assert _evaluated == []
    v = d["a"]
    assert _loaded
    assert _evaluated == ["100-99"]
    assert v == 1

if __name__ == "__main__":

    test_lazy_load()
    test_lazy_eval()
    test_lazy_load_eval()