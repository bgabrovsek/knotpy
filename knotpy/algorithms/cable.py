from knotpy.classes.planardiagram import Diagram
from string import ascii_letters

def _name(node, i, j):
    # name a node in the nxn lattice
    return f"{node}{i}{j}"

def cable(k:Diagram, n:int=2):

    if not all(isinstance(node, str) for node in k.nodes):
        raise ValueError("Can only cable diagrams with nodes of string type")

    c = type(k)()  # The n-cable knot

    # add crossings to c, a -> a00, a01, ...
    for node in k.crossings:
        for i in range(n):
            for j in range(n):
                c.add_crossing(_name(node, i, j))

    # TODO: what about vertices?


    # take care of all boundary
    for ep in k.endpoints:
        twin = k.twin(ep)
        for i in range(n):
            c.set_endpoint(
                endpoint_for_setting=(_name(ep.name, ep.pos, i), ep.pos),
                adjacent_endpoint=(_name(twin.name, i, twin.pos), twin.pos),
                create_using=type(twin),
                **twin.attr
            )

        for i in range(1, n-1):
            for j in range(1, n-1):
                c.set_endpoint(
                    endpoint_for_setting=(_name(ep.name, ep.pos, i), ep.pos),
                    adjacent_endpoint=(_name(twin.name, i, twin.pos), twin.pos),
                    create_using=type(twin),
                    **twin.attr
                )


if __name__ == "__main__":
    import knotpy as kp
    k = kp.knot("3_1")
    print(k)
    c = cable(k, 2)
    print(c)



