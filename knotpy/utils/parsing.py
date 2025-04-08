from string import ascii_letters
import re

__all__ = ["parse_arc", "parse_arcs", "parse_endpoint"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'


def parse_endpoint(endpoint: str):
    """
    Parse an endpoint string and return a tuple (letter, integer).
    
    :param endpoint: String representing an endpoint (e.g., "a9").
    :return: Tuple of (letter, integer) if valid.
    :raises ValueError: If the string is not in the correct format.
    """

    endpoint = endpoint.strip()

    if len(endpoint) != 2:
        raise ValueError(f"Invalid endpoint format: {endpoint}")

    letter, number = endpoint[0], endpoint[1]

    if letter not in ascii_letters:
        raise ValueError(f"Invalid letter in endpoint: {letter}")
    if not number.isdigit():
        raise ValueError(f"Invalid number in endpoint: {number}")

    return letter, int(number)


def parse_arc(arc: str):
    """
    Parse an arc string and return a tuple of two endpoint tuples.
    
    :param arc: String representing an arc (e.g., "a1b5").
    :return: Tuple of ((letter1, integer1), (letter2, integer2)) if valid.
    :raises ValueError: If the string is not in the correct format.
    """
    
    arc = arc.strip()

    if len(arc) < 4:
        raise ValueError(f"Invalid arc format: {arc}")

    return parse_endpoint(arc[:2]), parse_endpoint(arc[2:])


def parse_arcs(arcs: str):
    """
    Parse a string of arcs separated by commas and return a list of parsed arcs.

    :param arcs: String representing multiple arcs (e.g., "a6b6, a9u8").
    :return: List of tuples, each representing a parsed arc.
    :raises ValueError: If any arc is not in the correct format.
    """
    return [parse_arc(arc.strip()) for arc in arcs.split(",")]


def universal_list_of_lists_parser(input_str):
    # TODO: it does not work at all
    # Normalize and clean the input string
    s = input_str.strip()

    # If the input uses square or round brackets, find enclosed groups
    if any(c in s for c in '[]()'):
        # Replace round brackets with square brackets for consistency
        s = s.replace('(', '[').replace(')', ']')

        # Use regex to extract sublists inside brackets
        matches = re.findall(r'\[([^\[\]]+)\]', s)
    else:
        # Otherwise, treat comma-separated groups
        matches = s.split(',')

    result = []
    for m in matches:
        # Split each group by comma or whitespace
        items = re.split(r'[,\s]+', m.strip())
        if items and items != ['']:
            # Convert to int if possible
            group = []
            for item in items:
                try:
                    group.append(int(item))
                except ValueError:
                    group.append(item)
            result.append(group)



if __name__ == "__main__":
    # Test parse_endpoint
    try:
        print(parse_endpoint("a9"))  # Expected: ('a', 9)
        print(parse_endpoint("z1"))  # Expected: ('z', 10)
    except ValueError as e:
        print(f"parse_endpoint error: {e}")

    # Test parse_arc
    try:
        print(parse_arc("a1b5"))  # Expected: (('a', 1), ('b', 5))
        print(parse_arc("x8y3"))  # Expected: (('x', 8), ('y', 3))
    except ValueError as e:
        print(f"parse_arc error: {e}")

    # Test parse_arcs
    try:
        print(parse_arcs("a6b6, a9u8"))  # Expected: [(('a', 6), ('b', 6)), (('a', 9), ('u', 8))]
    except ValueError as e:
        print(f"parse_arcs error: {e}")

