


def min_elements_by(items, key):
    """
    Return all elements from the list that have the minimal value under the key function.

    Args:
        items (iterable): The list of elements to search.
        key (callable): A function that maps each element to a value to compare.

    Returns:
        list: A list of elements where key(item) is minimal.
    """
    if not items:
        return []

    values = [(item, key(item)) for item in items]
    min_val = min(val for _, val in values)
    return [item for item, val in values if val == min_val]