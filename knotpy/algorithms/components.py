__all__ = ['connected_components_nodes', 'number_of_connected_components', 'connected_components', ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from copy import deepcopy

from knotpy.utils.equivalence import EquivalenceRelation


def connected_components_nodes(self):
    er = EquivalenceRelation(self._adj)
    for v in self._adj:
        for u, u_pos in self._adj[v]:
            er[v] = u

    return er.classes()


def number_of_connected_components(self):
    return len(self._connected_components_nodes())


def connected_components(self):
    components = []
    for component_nodes in sorted(self._connected_components_nodes(), reverse=True):
        g = self.__class__()
        g.attr = deepcopy(self.attr)
        g._adj = {node: deepcopy(self._adj[node]) for node in component_nodes}
        g._node_attr = {node: deepcopy(self._node_attr[node]) for node in component_nodes}
        g._endpoint_attr = {deepcopy(ep): deepcopy(self._endpoint_attr[ep])
                            for ep in self._endpoint_attr if ep[0] in component_nodes}
        components.append(g)

    for g in components[1:]:
        g.framing = 0
    return components


if __name__ == "__main__":
    pass