import knotpy as kp

class DegreeView(DiDegreeView):
    """A DegreeView class to act as G.degree for a NetworkX Graph

    Typical usage focuses on iteration over `(node, degree)` pairs.
    The degree is by default the number of edges incident to the node.
    Optional argument `weight` enables weighted degree using the edge
    attribute named in the `weight` argument.  Reporting and iteration
    can also be restricted to a subset of nodes using `nbunch`.

    Additional functionality include node lookup so that `G.degree[n]`
    reported the (possibly weighted) degree of node `n`. Calling the
    view creates a view with different arguments `nbunch` or `weight`.

    Parameters
    ==========
    graph : NetworkX graph-like class
    nbunch : node, container of nodes, or None meaning all nodes (default=None)
    weight : string or None (default=None)

    Notes
    -----
    DegreeView can still lookup any node even if nbunch is specified.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> DV = G.degree()
    >>> assert DV[2] == 1
    >>> assert G.degree[2] == 1
    >>> assert sum(deg for n, deg in DV) == 4

    >>> DVweight = G.degree(weight="span")
    >>> G.add_edge(1, 2, span=34)
    >>> DVweight[2]
    34
    >>> DVweight[0]  #  default edge weight is 1
    1
    >>> sum(span for n, span in DVweight)  # sum weighted degrees
    70

    >>> DVnbunch = G.degree(nbunch=(1, 2))
    >>> assert len(list(DVnbunch)) == 2  # iteration over nbunch only
    """

    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return len(nbrs) + (n in nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values()) + (
            n in nbrs and nbrs[n].get(weight, 1)
        )

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                nbrs = self._succ[n]
                yield (n, len(nbrs) + (n in nbrs))
        else:
            for n in self._nodes:
                nbrs = self._succ[n]
                deg = sum(dd.get(weight, 1) for dd in nbrs.values()) + (
                    n in nbrs and nbrs[n].get(weight, 1)
                )
                yield (n, deg)
