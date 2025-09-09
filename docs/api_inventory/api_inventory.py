# save as api_inventory.py and run: python api_inventory.py your_pkg > api_inventory.json
import importlib, pkgutil, inspect, json, sys, types

pkg_name = sys.argv[1]
pkg = importlib.import_module(pkg_name)

def is_public(name): 
    return not name.startswith("_")

def obj_info(obj):
    kind = ("class" if inspect.isclass(obj) else
            "function" if inspect.isfunction(obj) else
            "module" if inspect.ismodule(obj) else
            "other")
    try:
        sig = str(inspect.signature(obj)) if (inspect.isfunction(obj) or inspect.isclass(obj)) else None
    except Exception:
        sig = None
    doc = inspect.getdoc(obj) or ""
    doc1 = doc.splitlines()[0] if doc else ""
    return {"kind": kind, "signature": sig, "doc1": doc1}

def walk_modules(root):
    seen = set()
    results = {}
    stack = [root]
    while stack:
        m = stack.pop()
        if m.__name__ in seen: 
            continue
        seen.add(m.__name__)
        entry = {"objects": {}, "submodules": []}
        for name, obj in vars(m).items():
            if is_public(name):
                entry["objects"][name] = obj_info(obj)
        if hasattr(m, "__path__"):
            for modinfo in pkgutil.walk_packages(m.__path__, m.__name__ + "."):
                try:
                    sub = importlib.import_module(modinfo.name)
                    entry["submodules"].append(modinfo.name)
                    stack.append(sub)
                except Exception:
                    # skip broken imports; examples will mock these if needed
                    pass
        results[m.__name__] = entry
    return results

print(json.dumps(walk_modules(pkg), indent=2, sort_keys=True))
