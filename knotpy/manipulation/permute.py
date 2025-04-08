def permute_node(k, node, permutation):
    """Permute the endpoints of the node of knot k. For example, if p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,3,1]),
    and if node has endpoints [a, b, c, d] (ccw) then the new endpoints will be [a, d, b, c].
    :param k: knot diagram
    :param node: node of which we permute its endpoints
    :param permutation: permutation given as a dict or list/tuple
    :return: None
    TODO: are there problems regarding endpoint attributes?
    TODO: check if it works for loops (probably does not)
    TODO: make this faster, since it a frequently called operation in canonical() and consumes a lot of tottime and cumtime
    """

    adj_endpoints = [adj_ep for adj_ep in k.nodes[node]]  # save old endpoints, maybe enough just list(...)
    #print(k, "node", node, "perm", permutation)
    node_endpoint_inst = [k.twin(adj_ep) for adj_ep in adj_endpoints]
    for pos, adj_ep in enumerate(adj_endpoints):
        if adj_ep.node != node:  # no loop
            # set adjacent
            k.set_endpoint(endpoint_for_setting=(node, permutation[pos]),
                           adjacent_endpoint=(adj_ep.node, adj_ep.position),
                           create_using=type(adj_ep),
                           **adj_ep.attr)
            # set self
            k.set_endpoint(endpoint_for_setting=adj_ep,
                           adjacent_endpoint=(node, permutation[pos]),
                           create_using=type(node_endpoint_inst[pos]),
                           **node_endpoint_inst[pos].attr)
        else:
            # set adjacent
            k.set_endpoint(endpoint_for_setting=(node, permutation[pos]),
                           adjacent_endpoint=(adj_ep.node, permutation[adj_ep.position]),
                           create_using=type(adj_ep),
                           **adj_ep.attr)


    return

    # convert list/tuple permutation to dict
    if isinstance(p, list) or isinstance(p, tuple):
        p = dict(enumerate(p))

    #invp = inverse_dict(p)

    old_node_data = list(k.nodes[node])  # save old node ccw sequence since it can override
    for pos, ep in enumerate(old_node_data):
        #print("old_node_data[pos]", old_node_data[pos], type(old_node_data[pos]))
        # set endpoint from adjacent crossing
        #print(type(ep))
        if DEBUG: print("setting", ep, "to", (node, p[pos]))
        k.set_endpoint(
            endpoint_for_setting=ep,
            adjacent_endpoint=(node, p[pos]),
            create_using=type(old_node_data[pos]),  # copies the type and "old" attributes
            )
        # set endpoint from crossing
        if DEBUG: print("Setting", node,p[pos], "to", ep)
        k.nodes[node][p[pos]] = ep

    if DEBUG: print("result", k)
