"""
DT (Dowker–Thistlethwaite) notation.
"""

__all__ = ["from_dt_notation"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from itertools import product

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.endpoint import IngoingEndpoint, OutgoingEndpoint
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.topology import is_knot, is_link
from knotpy.utils.parsing import parse_spaced_rows
from knotpy.utils.list_utils import flatten_nested_list
from knotpy.algorithms.naming import number_to_alpha


def from_dt_notation(notation, oriented=False):
    """
    :param notation: dictionary of lists of tuples or a string that evaluates to this
    :param oriented:
    :return: PlanarGraph object
    """

    # parse the input
    try:
        # if notation is a string, convert it to a tuple
        if isinstance(notation, str):
            notation = parse_spaced_rows(notation)
        if not notation:
            return OrientedPlanarDiagram() if oriented else PlanarDiagram()
        # wrap a knot notation to a 1-component link notation
        if all(isinstance(value, int) for value in notation):
            notation = [notation]
    except ValueError:
        raise ValueError(f"Invalid DT notation {notation}") from None

    flat_notation = flatten_nested_list(notation)
    flat_notation_unsigned = [abs(v) for v in flat_notation]
    even_labels = range(1, 2 * len(flat_notation_unsigned), 2)
    labels = dict(zip(even_labels, flat_notation_unsigned)) | dict(zip(flat_notation_unsigned, even_labels))  # unsigned label pairs
    under = dict(zip(even_labels, [v < 0 for v in flat_notation])) | dict(zip(flat_notation_unsigned, [v > 0 for v in flat_notation]))  # assign to every label if it is under (True) or over (False)

    crossing_counter = -1  # current crossing (0 = "a", 1 = "b", ...)

    # endpoint_options = {}  # keys are labels, values are possible crossing/position pairs
    # endpoints_in = {}  # keys are labels, values are pairs (crossing, position)
    # endpoints_out = {}  # keys are labels, values are pairs (crossing, position)

    """
    There are usually multiple ways to attach a label to a crossing. Place all options on the stack that consists of:
    1. endpoint_options dict  - keys are labels, values are possible crossing/position pairs
    2. endpoint_in dict - keys are labels, values are pairs (crossing, position)
    3. endpoint_out dict - keys are labels, values are pairs (crossing, position)
    """

    endpoint_options = {}
    endpoints_in = {}
    endpoints_out = {}

    for label, adj_label in labels.items():
        if label not in endpoint_options:
            c = number_to_alpha(crossing_counter := crossing_counter + 1)
            endpoints_in[label] = (c, 0 if under[label] else 1)  # choose positions 0 or 1 for ingoing label
            endpoints_out[label] = (c, 2 if under[label] else 3)  # choose positions 2 or 3 for outgoing label
            endpoint_options[adj_label] = {(c, 1), (c, 3)} if under[label] else {(c, 0), (c, 2)}  # new options for adjacent labels

    # iterate over all possible options of attachments, works in python 3.7+ (insert order preserved)

    # TODO: we can remove 1/2 of the options (symmetry), i.e. choice of 1st assignment
    for values_option in product(*endpoint_options.values()):
        endpoints = dict(zip(endpoint_options.keys(), values_option))
        ep_in = endpoints_in | endpoints
        ep_out = endpoints_out | endpoints
        print(ep_in, ep_out)








    # stack = deque([({}, {}, {})])
    #
    # for label, adj_label in labels.items():
    #     new_stack = deque()
    #     for endpoint_options, endpoints_in, endpoints_out in stack:
    #         if label not in endpoint_options:
    #             crossing = number_to_alpha(crossing_counter := crossing_counter + 1)
    #             endpoints_in[label] = (crossing, 0 if under[label] else 1)  # choose positions 0 or 1 for ingoing label
    #             endpoints_out[label] = (crossing, 2 if under[label] else 3)  # choose positions 2 or 3 for outgoing label
    #             endpoint_options[adj_label] = {(crossing, 1), (crossing, 3)} if under[label] else {(crossing, 0), (crossing, 2)}  # new options for adjacent labels
    #             new_stack.append((endpoint_options, endpoints_in, endpoints_out))
    #         else:
    #             # label exists and there are two options how to attach it
    #             ep1, ep2 = endpoint_options[label]
    #             new_stack.append(
    #                 (
    #
    #                 )
    #             )







def to_dt_notation(k: PlanarDiagram | OrientedPlanarDiagram) -> tuple:
    if not is_link(k):
        raise ValueError("DT notation is only defined for knots")
    k = orient(k) if not k.is_oriented() else k.copy()

    labels = {}  # keys are labels (1, 2, ...), values are (crossing, position % 2), component
    labels_reversed = {}  # keys are (node, position % 2), labels are label index (1, 2, ...)
    component = -1
    while len(labels_reversed) < k.number_of_crossings * 2:
        component += 1
        # Start with the ingoing endpoint of the minimal unused crossings.
        count_used_crossings = {}
        available_crossings = []
        crossing = min(k.crossings)  # TODO: this does not work for links
        ep = k.endpoint_from_pair((crossing, "ingoing over"))
        while (ep.node, ep.position % 2) not in labels_reversed:
            labels[len(labels) + 1] = (ep.node, ep.position % 2, component)
            labels_reversed[(ep.node, ep.position % 2)] = len(labels)
            ep = k.twin((ep.node, (ep.position + 2) % 4))  # jump over to the next endpoint

    dt_notation_link = [[] for _ in range(component + 1)]
    for component_index, notation in enumerate(dt_notation_link):
        for even_label in range(1, 2 * k.number_of_crossings, 2):
            crossing, position, label_component = labels[even_label]
            if label_component != component_index:
                continue
            odd_label = labels_reversed[(crossing, 1 - position)]
            notation.append(odd_label * (1 if position else -1))
    return tuple(dt_notation_link[0]) if len(dt_notation_link) == 1 else tuple(tuple(_) for _ in dt_notation_link)

if __name__ == '__main__':

    n = "6 -8, -10 12 -14 2 -4"
    from_dt_notation(n)

    #
    #
    # def wrap_list(data):
    #     """
    #     If data is a list of integers, return [[...]].
    #     If it's empty or [[]], return None.
    #     """
    #     if not data or data == [[]]:
    #         return None
    #     if all(isinstance(x, int) for x in data):
    #         return [data]
    #     return data
    #
    #
    # print(parse_input("1 2 3"))  # ➜ [1, 2, 3]
    # print(parse_input("1 2 3, 4 5 -6"))  # ➜ [[1, 2, 3], [4, 5, -6]]
    # print(parse_input("1 2 3 ; 4 5 -6"))  # ➜ [[1, 2, 3], [4, 5, -6]]
    #
    # print(wrap_list([1, 2, 3]))  # ➜ [[1, 2, 3]]
    # print(wrap_list([]))  # ➜ None
    # print(wrap_list([[]]))  # ➜ None
    # print(wrap_list([[1, 2], [3]]))  # ➜ [[1, 2], [3]]