
import knotpy


# from knotpy.generators import simple


### DATA -> SPATIAL GRAPH

def pg_from_list(data, create_using=None):
    pd = knotpy.classical.empty_pd(0, create_using)
    return knotpy
    pass


def to_pg(data, create_using=None):
    """Create planar diagram from data and store to create using. """

    if isinstance(data, list):
        try:
            return pg_from_list(data, create_using)
        except:
            raise TypeError("create_using is not a valid knotpy type or instance")

    pass

"""
def node_from_list(data, create_using=None):
    pd = simple.empty_node(0, create_using)
    return knotpy
    pass

def to_node(data, create_using=None):
    # if hasattr(data, "is_strict"):
    if isinstance(data, list):
        try:
            return node_from_list(data, create_using)
        except:
            raise TypeError("create_using is not a valid node type or instance")

    pass
"""