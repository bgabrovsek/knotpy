# class LazyLoadList(list):
#     """
#     A list that defers loading its data until first accessed.
#
#     Useful for delaying expensive list computations or loads (e.g., from disk or computation-heavy routines)
#     until actually needed. The `load_function` should return a list or iterable.
#     """
#
#     def __init__(self, load_function=None, *args, **kwargs):
#         """
#         Parameters
#         ----------
#         load_function : Callable or None
#             A function returning the list (or iterable) to be loaded lazily.
#             If None, the list is assumed to be preloaded via `args` or `kwargs`.
#         """
#         super().__init__(*args, **kwargs)
#         self._load_function = load_function
#         self._data_loaded = load_function is None
#
#     def _ensure_loaded(self):
#         if not self._data_loaded:
#             self.extend(self._load_function())
#             self._data_loaded = True
#
#     def __getitem__(self, index):
#         self._ensure_loaded()
#         return super().__getitem__(index)
#
#     def __setitem__(self, index, value):
#         self._ensure_loaded()
#         return super().__setitem__(index, value)
#
#     def __iter__(self):
#         self._ensure_loaded()
#         return super().__iter__()
#
#     def __len__(self):
#         self._ensure_loaded()
#         return super().__len__()
#
#     def __contains__(self, item):
#         self._ensure_loaded()
#         return super().__contains__(item)
#
#     def __repr__(self):
#         self._ensure_loaded()
#         return f"LazyLoadList({super().__repr__()})"
#
#     def append(self, item):
#         self._ensure_loaded()
#         return super().append(item)
#
#     def extend(self, iterable):
#         self._ensure_loaded()
#         return super().extend(iterable)
#
#     def insert(self, index, item):
#         self._ensure_loaded()
#         return super().insert(index, item)
#
#     def pop(self, index=-1):
#         self._ensure_loaded()
#         return super().pop(index)
#
#     def clear(self):
#         self._ensure_loaded()
#         return super().clear()
#
#     def index(self, value, *args):
#         self._ensure_loaded()
#         return super().index(value, *args)
#
#     def count(self, value):
#         self._ensure_loaded()
#         return super().count(value)
#
#     def sort(self, *args, **kwargs):
#         self._ensure_loaded()
#         return super().sort(*args, **kwargs)
#
#     def reverse(self):
#         self._ensure_loaded()
#         return super().reverse()
#
#     def reload(self):
#         """Clear and reload the list (if a load function is available)."""
#         if self._load_function is not None:
#             super().clear()
#             self._data_loaded = False
#             self._ensure_loaded()
#
#
#
# class LazyEvalDict(dict):
#     """
#     A dictionary that evaluates values lazily upon access.
#
#     This class extends the standard Python dictionary to support lazy evaluation
#     of its values. A user-defined function is applied to the value associated
#     with a key the first time that key is accessed. Subsequent accesses return
#     the already-evaluated value without invoking the evaluation function again.
#     This approach is beneficial in scenarios where the value computation is
#     expensive, and the result is needed only on demand.
#
#     Attributes:
#         _eval_function: Callable function used to lazily evaluate values.
#         _evaluated_keys: Set of keys whose values have already been evaluated.
#     """
#     def __init__(self, eval_function, *args, **kwargs):
#         """
#         Initializes an instance of a class that performs actions based on a provided evaluation function.
#         Ensures the evaluation function is callable and prepares an internal state to track evaluated keys.
#
#         Parameters
#         ----------
#         eval_function : Callable
#             A callable used to perform evaluations. Must be passed and checked for
#             its callable nature.
#         *args
#             Positional arguments passed to the base class initializer.
#         **kwargs
#             Keyword arguments passed to the base class initializer.
#
#         Raises
#         ------
#         TypeError
#             If `eval_function` is not callable.
#         """
#         super().__init__(*args, **kwargs)
#         if not callable(eval_function):
#             raise TypeError("eval_function must be callable")
#         self._eval_function = eval_function
#         self._evaluated_keys = set()
#
#     def __getitem__(self, key):
#         # Evaluate the value of the key if it is not already evaluated.
#         if key not in self._evaluated_keys:
#             super().__setitem__(key, self._eval_function(super().__getitem__(key)))
#             self._evaluated_keys.add(key)
#         return super().__getitem__(key)
#
#     def values(self):
#         """Return all values, forcing evaluation of any unevaluated entries."""
#         for key in self:
#             _ = self[key]  # Ensure all values are evaluated
#         return super().values()
#
#     def items(self):
#         """Return all key-value pairs, forcing evaluation of any unevaluated entries."""
#         for key in self:
#             _ = self[key]  # Ensure all values are evaluated
#         return super().items()
#
#     def __repr__(self):
#         return f"LazyEvalDict(keys={dict().keys()})"
#
#
#
# class LazyLoadDict(dict):
#     """
#     LazyLoadDict is a custom dictionary class that defers data loading until it is first accessed,
#     optimizing resource usage by delaying expensive initialization operations. It mimics the behavior
#     of a standard Python dictionary while incorporating lazy loading functionality.
#
#     This makes it ideal for scenarios where loading data is expensive, and you want to defer the operation
#     until it’s actually needed.
#     """
#
#     def __init__(self, load_function, *args, **kwargs):
#         """
#         Initializes an instance with a function to load data, along with any additional arguments or keyword arguments.
#
#         Parameters
#         ----------
#         load_function : Callable or None
#             A function responsible for loading the data. The function should return a dictionary or a list or tuples
#             representing the dictionary. If None, the data is assumed to be preloaded.
#         *args :
#             Additional positional arguments passed to the superclass.
#         **kwargs :
#             Additional keyword arguments passed to the superclass.
#
#         Attributes
#         ----------
#         _data_loaded : bool
#             A flag indicating whether the data has already been loaded.
#         _load_function : Callable or None
#             The function used to load data. If None, no loading function is used.
#         """
#         super().__init__(*args, **kwargs)
#         self._data_loaded = load_function is None
#         self._load_function = load_function
#
#     def _ensure_loaded(self):
#         if not self._data_loaded:
#             self.update(self._load_function())
#             self._data_loaded = True
#
#     def __getitem__(self, key):
#         self._ensure_loaded()
#         return super().__getitem__(key)
#
#     def __setitem__(self, key, value):
#         self._ensure_loaded()
#         super().__setitem__(key, value)
#
#     def __contains__(self, key):
#         self._ensure_loaded()
#         return super().__contains__(key)
#
#     def __iter__(self):
#         self._ensure_loaded()
#         return super().__iter__()
#
#     def get(self, key, default=None):
#         self._ensure_loaded()
#         return super().get(key, default)
#
#     def pop(self, key, default=None):
#         self._ensure_loaded()
#         return super().pop(key, default)
#
#     def keys(self):
#         self._ensure_loaded()
#         return super().keys()
#
#     def values(self):
#         self._ensure_loaded()
#         return super().values()
#
#     def items(self):
#         self._ensure_loaded()
#         return super().items()
#
#     def __len__(self):
#         self._ensure_loaded()
#         return super().__len__()
#
#     def __repr__(self):
#         self._ensure_loaded()
#         return f"LazyLoadDict({super().__repr__()})"
#
