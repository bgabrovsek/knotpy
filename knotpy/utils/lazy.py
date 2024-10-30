"""
Lazy data module
"""
__all__ = ["LazyLoadDict", "LazyDict"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class LazyLoadDict(dict):
    """
    LazyDict is a custom dictionary class that delays loading its data until it is accessed for the first time. It inherits
    from Python’s built-in dict, providing all standard dictionary methods while ensuring efficient, on-demand data
    initialization. This makes it ideal for scenarios where loading data is expensive, and you want to defer the operation
    until it’s actually needed.
    """
    def __init__(self, load_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_loaded = load_function is None
        self._load_function = load_function

    def _ensure_loaded(self):
        if not self._data_loaded:
            self.update(self._load_function())
            self._data_loaded = True

    def __getitem__(self, key):
        self._ensure_loaded()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __contains__(self, key):
        self._ensure_loaded()
        return super().__contains__(key)

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def get(self, key):
        self._ensure_loaded()
        return super().get(key)

    def keys(self):
        self._ensure_loaded()
        return super().keys()

    def values(self):
        self._ensure_loaded()
        return super().values()

    def items(self):
        self._ensure_loaded()
        return super().items()

    def __len__(self):
        self._ensure_loaded()
        return super().__len__()


class LazyDict(LazyLoadDict):
    """LazyEvalDict is a custom dictionary that extends Python’s built-in dict, designed for deferred (lazy) evaluation
    of values. It allows users to associate keys with functions that are only executed when the corresponding values are
    accessed for the first time, reducing unnecessary computations. After the initial evaluation, the results are cached
    for future access, providing efficiency for scenarios where value conversion is slow or resource-intensive.
    This class is ideal for cases where data processing should be postponed until it’s truly needed.
    TODO: if we update, the values should be removed from _evaluated


    """

    def __init__(self, eval_function, load_function=None,  *args, **kwargs):
        """
        Initialize with a dictionary of evaluation functions.

        :param eval_functions: A dictionary where keys are the expected keys and
                               values are the functions to be used for lazy evaluation.
                               If a function is given, it loads using the function for any key
        :param args, kwargs: Additional arguments to initialize the dict.
        #aliases are for keys, for example, we can access key "Jones" and we really access "Jones polynomial"
        """
        super().__init__(load_function=load_function, *args, **kwargs)
        self._eval_function = eval_function
        #self.eval_keys_aliases = eval_keys_aliases
        self._evaluated = {}

    def _ensure_loaded(self):
        if not self._data_loaded:
            self.update(self._load_function())
            self._data_loaded = True

    def __setitem__(self, key, value):
        """
        Set a value in the dictionary. If the key has an associated evaluation function,
        the value will be evaluated lazily.
        """
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __getitem__(self, key):
        """
        Get the value from the dictionary. If the value has an associated evaluation function
        and has not yet been evaluated, it will be evaluated now and the result will be stored.
        """
        # if self.eval_keys_aliases:
        #     key = self.eval_keys_aliases.get(key, key)

        self._ensure_loaded()
        if key not in self._evaluated:
            # Perform lazy evaluation if the key is in self._eval_functions
            if callable(self._eval_function):
                super().__setitem__(key, self._eval_function(super().__getitem__(key)))
            elif key in self._eval_function:
                str_value = super().__getitem__(key)
                if str_value:
                    super().__setitem__(key, self._eval_function[key](str_value))
                else:
                    super().__setitem__(key, None)

        self._evaluated[key] = True

        return super().__getitem__(key)

    # def get(self, key, default=None):
    #     """Get a value with a default if the key does not exist."""
    #     try:
    #         return self[key]
    #     except KeyError:
    #         return default

    def values(self):
        """Return all values, forcing evaluation of any unevaluated entries."""
        self._ensure_loaded()
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return super().values()

    def items(self):
        """Return all key-value pairs, forcing evaluation of any unevaluated entries."""
        self._ensure_loaded()
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return super().items()

    def __repr__(self):
        self._ensure_loaded()
        return f"LazyEvalDict({super().__repr__()})"
