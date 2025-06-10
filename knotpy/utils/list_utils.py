
def _flatten_nested_list(nested):
    """
    Recursively flattens a list of arbitrary depth into a flat list.

    Example:
        [1, [2, [3, 4], 5], 6] -> [1, 2, 3, 4, 5, 6]
    """
    for item in nested:
        if isinstance(item, list):
            yield from _flatten_nested_list(item)
        else:
            yield item

def flatten_nested_list(nested):
    return list(_flatten_nested_list(nested))