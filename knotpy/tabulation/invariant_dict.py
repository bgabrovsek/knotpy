from collections import Counter

__all__ = ['InvariantDict']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

class InvariantDict(dict):
    def __init__(self, func):
        """
        Initializes the dictionary with a function, a list/tuple of functions,
        or a dictionary where keys are computed invariant values and values are objects (diagrams).

        :param func: A function, list/tuple of functions, or a dictionary of named invariants.
        """
        if callable(func):  # Single function
            self.funcs = func
            self.invariant_names = None
        elif isinstance(func, (list, tuple)) and all(callable(f) for f in func):  # List/Tuple of functions
            self.funcs = tuple(func)
            self.invariant_names = None
        elif isinstance(func, dict) and all(callable(f) for f in func.values()):  # Dictionary of named functions
            self.funcs = tuple(func.values())
            self.invariant_names = tuple(func.keys())
        else:
            raise TypeError("func must be a callable, a list/tuple of callables, or a dictionary of named invariants.")

        super().__init__()  # Initialize as a dictionary

    def _compute_key(self, value):
        """Computes the key based on the stored function(s)."""
        # if self.invariant_names:
        #     return {name: f(value) for name, f in zip(self.invariant_names, self.funcs)}
        if callable(self.funcs):
            return self.funcs(value)
        else:
            return tuple(f(value) for f in self.funcs)

    def __setitem__(self, key, value):
        """Adds a value to the computed key's set."""
        computed_key = self._compute_key(key)
        if computed_key not in self:
            super().__setitem__(computed_key, set())
        self[computed_key].add(value)

    def append(self, value):
        """Appends a value to the computed key's set."""
        computed_key = self._compute_key(value)
        if computed_key not in self:
            super().__setitem__(computed_key, set())
        self[computed_key].add(value)

    def extend(self, values):
        """Extends the dictionary with multiple values."""
        for value in values:
            self.append(value)

    def stats(self):
        """Return a dictionary {length: count} indicating how many values have each length."""
        return dict(Counter(len(v) for v in self.values()))

    def __repr__(self):
        """Returns a string representation of the dictionary."""
        return f"{self.__class__.__name__}({dict(self)})"  # Convert to regular dict for cleaner output

# Example usage:
if __name__ == "__main__":
    # Example 1: Grouping numbers by a single function (parity)
    inv_dict1 = InvariantDict(lambda x: x % 2)
    inv_dict1.append(2)
    inv_dict1.append(3)
    inv_dict1.append(4)
    inv_dict1.append(9)
    inv_dict1.extend([6, 7, 10])
    print("Example 1:", inv_dict1)  # Should group numbers by parity (even/odd)

    # Example 2: Grouping numbers by multiple functions (parity and remainder when divided by 3)
    inv_dict2 = InvariantDict([lambda x: x % 2, lambda x: x % 3])
    inv_dict2.append(2)
    inv_dict2.append(3)
    inv_dict2.append(4)
    inv_dict2.append(9)
    inv_dict2.extend([6, 7, 10])
    print("Example 2:", inv_dict2)  # Should group numbers by (x % 2, x % 3)

    # Example 3: Grouping with named invariants
    inv_dict3 = InvariantDict({
        "parity": lambda x: x % 2,
        "mod3": lambda x: x % 3
    })
    inv_dict3.append(2)
    inv_dict3.append(3)
    inv_dict3.append(4)
    inv_dict3.append(9)
    inv_dict3.extend([6, 7, 10])
    print("Example 3:", inv_dict3)  # Should group numbers by {"parity": ..., "mod3": ...}