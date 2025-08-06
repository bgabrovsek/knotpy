import knotpy as kp


# TODO: assert

if __name__ == '__main__':
    k = kp.knot("3_1")
    print(k)

    # access crossing information by node name
    # print("crossing", k.nodes["a"])
    # print("crossing", k["a"])

    # get opposite endpoint (twin) of an endpoint (by Endpoint instance or pair)
    ep_instance = k.nodes["a"][0]
    ep_pair = ("c", 3)
    print("Twin of", ep_instance, "is", k.twin(ep_instance))
    print("Twin of", ep_pair, "is", k.twin(ep_pair))
    print("Twin of", ep_instance, "is", k.nodes[ep_instance.node][ep_instance.position])
    print("Twin of", ep_instance, "is", k.nodes[ep_instance])


    # get endpoint from the pair
    print("Endpoint", ep_pair, "is", k.endpoint_from_pair(ep_pair))
    print("Endpoint", ep_instance, "is", k.endpoint_from_pair(ep_instance))  # also works as an identity for an endpoint

    # get endpoint from the pair
    print("Identity of", ep_pair, "is", k.endpoint_from_pair(ep_pair))
    print("Identity of", ep_instance, "is", k.endpoint_from_pair(ep_instance))  # also works as an identity for an endpoint

    # jump over crossing
    # print("Jump of", ep_pair, "is", k.jump_over_node(ep_pair))
    # print("Jump of", ep_instance, "is", k.jump_over_node(ep_pair))  # also works as an identity for an endpoint

    #
    # k.adjacent()
    # print("adjacent endpoint", k[e])
    # print(k.nodes[e])
    # print("adjacent endpoint", k.endpoints["a"])
    # print("adjacent endpoint", k.endpoints[e])

