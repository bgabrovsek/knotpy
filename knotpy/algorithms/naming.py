import string

_reverse_alphabet = {char: index for index, char in enumerate(string.ascii_letters)}
_base = len(string.ascii_letters)

def generate_node_names(number_of_nodes:int):
    return [number_to_alpha(i) for i in range(number_of_nodes)]

def _alpha_to_number(s: str):
    """ Convert ASCII string to number, e.g. "a" -> 0, "b" -> 1, "Z" -> 51, "aa" -> 52,... """
    index = 0
    for c in s:
        index = index * _base + _reverse_alphabet[c]
    # Offset for all shorter strings
    offset = sum(_base**i for i in range(1, len(s)))
    return index + offset

def number_to_alpha(n: int) -> str:
    """ Convert number to ASCII string, e.g. 0 -> "a", 1 -> "b", 51 -> "Z", 52 -> "aa", ... """
    # Determine length of string based on offset
    length = 1
    total = _base
    while n >= total:
        length += 1
        n -= total
        total = _base ** length

    # Convert number to base-_base string of given length
    chars = []
    for _ in range(length):
        n, rem = divmod(n, _base)
        chars.append(string.ascii_letters[rem])
    return ''.join(reversed(chars))

def _is_alpha(s: str) -> bool:
    return s.isalpha() and s.isascii()


def unique_new_node_name(k):
    """Returns a natural next available node names for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if len(k.nodes) == 0:
        return number_to_alpha(0)

    # Check if nodes are integers
    if all(isinstance(node, int) for node in k.nodes):
        return max(k.nodes) + 1

    # Assume nodes are strings
    max_number = max(_alpha_to_number(node) for node in k.nodes if _is_alpha(node))
    return number_to_alpha(max_number + 1)

def multiple_unique_new_node_names(k, count):
    """Returns a natural next available node names for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if len(k.nodes) == 0:
        return [number_to_alpha(i) for i in range(count)]

    # Check if nodes are integers
    if all(isinstance(node, int) for node in k.nodes):
        return max(k.nodes) + 1

    # Assume nodes are strings
    max_number = max(_alpha_to_number(node) for node in k.nodes if _is_alpha(node))
    return [number_to_alpha(max_number + 1 + i) for i in range(count)]
