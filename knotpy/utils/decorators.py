from sympy import symbols, Symbol


# def knotted_structure(*node_types):
#     def wrapper(cls):
#         setattr(cls, "_allowed_node_types", set(node_types))
#
#         def inner_wrapper(*args, **kwargs):
#             result = cls(*args, **kwargs)
#             return result
#         return cls
#     return wrapper

#@knottted_structure(Crossing, Node)

def single_variable_invariant(default_variable):
    """Decorator for a single-variable invariant that converts the second argument of the invariant to a sympy symbol.
    The invariant is therefore of the form "def invariant_func(obj, variable, ...)". If function (invariant) is called
    by keyword argument, the keyword argument with key "variable" is assumed. If the "variable" key is not in the kwargs
    dictionary, the default variable default_variable is added to kwargs."""

    def inner(invariant_func):

        def _to_variable(arg):
            return arg if isinstance(arg, Symbol) else symbols(arg)

        def wrapper(*args, **kwargs):
            if len(args) >= 2:
                args = args[:1] + (_to_variable(args[1]),) + args[2:]
            else:
                kwargs["variable"] = _to_variable(kwargs["variable"] if "variable" in kwargs else default_variable)
            return invariant_func(*args, **kwargs)
        return wrapper

    return inner


def multi_variable_invariant(default_variables):
    """Decorator for a multi-variable invariant that converts the second argument of the invariant to a tuple of sympy
    symbols. The invariant is therefore of the form "def invariant_func(obj, variables, ...)". If function (invariant)
    is called by keyword argument, the keyword argument with key "variables" is assumed. If the "variables" key is not
    in the kwargs dictionary, the default variables default_variables is added to kwargs."""

    def inner(invariant_func):

        def _to_variables(arg):
            return tuple(var if isinstance(var, Symbol) else symbols(var) for var in arg)

        def wrapper(*args, **kwargs):
            if len(args) >= 2:
                args = args[:1] + (_to_variables(args[1]),) + args[2:]
            else:
                kwargs["variables"] = _to_variables(kwargs["variables"] if "variables" in kwargs else default_variables)
            return invariant_func(*args, **kwargs)
        return wrapper

    return inner

