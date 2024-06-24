from itertools import chain
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint


def copy_and_move_arc(k: PlanarDiagram, arc_dicts: list):
    """Creates a new arc for each dictionary in the list arc_dicts. A new arc is represented by a dictionary
    {old_endpoint_1: new_endpoint_1, old_endpoint_2: new_endpoint_2}.

    For example, if the dictionary is {a0i: b0, c1o: d2}, in the diagram node incidency, the following changes are made:
    a[c1o,...], c[...,a0i,...] is changed to b[d2o,...], d[...,...,b0i,...] (attributes are copied from key to value).
    The endpoints of a and c are not removed and stay as they were (unless overwritten by another dict).

    Keys must be Endpoint objects, values should be endpoint pairs.

    Method is non-stable (can damage the realizability of the diagram).
    :param k: planar diagram
    :param arc_dicts:
    :return:
    """

    print(arc_dicts)

    # fill the dictionary where only one endpoint is given. The dictionary should include the endpoints of the full arc.
    # TODO: simplify
    joined_dict = {key: d[key] for d in arc_dicts for key in d}  # dictionary of all endpoints
    new_arc_dicts = []
    for arc_dict in arc_dicts:
        if len(arc_dict) == 1:
            ep, = arc_dict  # get the key endpoint
            if ep not in joined_dict:  # did we remove the endpoint, since we assigned another arc to contain it?
                continue
            twin = k.twin(ep)
            if twin in joined_dict:
                arc_dict[twin] = joined_dict[twin]
                del joined_dict[twin]  # remove the dictionary
            else:
                arc_dict[twin] = (twin.node, twin.position)

        new_arc_dicts.append(arc_dict)
        #print("   ", arc_dict)
    #print("DICT", arc_dicts)
    #print("NEW ", arc_dicts)

    print(new_arc_dicts)

    # start copying and reassigning the endpoints
    for arc_dict in new_arc_dicts:
        old_ep1, old_ep2 = arc_dict
        new_ep1, new_ep2 = arc_dict.values()

        # new_ep2 copies type and attributes from old_ep2
        k.set_endpoint(endpoint_for_setting=new_ep1, adjacent_endpoint=new_ep2, create_using=old_ep2, **old_ep2.attr)
        # new_ep1 copies type and attributes from old_ep1
        k.set_endpoint(endpoint_for_setting=new_ep2, adjacent_endpoint=new_ep1, create_using=old_ep1, **old_ep1.attr)






