import string
from collections import defaultdict

_is_letter_but_not_Z = defaultdict(bool, {letter: True for letter in string.ascii_letters[:-1]})
_next_letter = defaultdict(bool, {string.ascii_letters[i]: string.ascii_letters[i + 1] for i in range(51)})



def unique_new_node_name(k, default="a"):
    """Returns a natural next available node name for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if not k.number_of_nodes:
        return default

    if all(_is_letter_but_not_Z[node] for node in k.nodes):
        return _next_letter[max(k.nodes, key=str.swapcase)]

    return max((node for node in k.nodes if isinstance(node, int)), default=0)


def name_for_next_node_generator(k, count=None, default="a"):
    """Returns a natural next available node name for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if not count:
        return

    new_node = unique_new_node_name(k)

    for _ in range(count-1):
        yield new_node
        if isinstance(new_node, int):
            new_node += 1
        else:
            new_node = _next_letter[new_node] if _is_letter_but_not_Z[new_node] else 0



def unique_temporary_new_node_name(d, base_key="temp"):
    """
    Find a unique key in d (dict) by appending underscores as needed.
    Args:
        d (dict): The dictionary (or similar).
        base_key (str): The base key to append underscores to.

    Returns:
        str: A unique key not already present in `d`.
    """
    unique_key = "_" + base_key
    while unique_key in d:
        unique_key = f"_{unique_key}"
    return unique_key