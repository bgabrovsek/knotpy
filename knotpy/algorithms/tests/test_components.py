
import pytest

import knotpy as kp

def test_link_components():

    k = kp.from_knotpy_notation("('SpatialGraph', {'name': 't0_1(0)'}, [('Vertex', 'a', (('Endpoint', 'b', 0, {'color': 1}), ('Endpoint', 'b', 1, {})), {}), ('Vertex', 'b', (('Endpoint', 'a', 0, {'color': 1}), ('Endpoint', 'a', 1, {'attr': {}})), {}), ('Vertex', 'c', (('Endpoint', 'd', 0, {}),), {}), ('Vertex', 'd', (('Endpoint', 'c', 0, {}),), {})])")

    assert kp.number_of_link_components(k) == 2



#
# from knotpy.algorithms.components import link_components_endpoints, path_from_endpoint
# from knotpy.algorithms.region_algorithms import regions
# from knotpy.notation.pd import from_pd_notation
#
# trefoil = from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]", "knotinfo")
# print(trefoil)
# print(list(regions(trefoil)))
#
# k = from_pd_notation("[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]", "knotinfo")
# print(k)
# print(link_components_endpoints(k))
#
# l = from_pd_notation("[[6, 1, 7, 2], [10, 7, 5, 8], [4, 5, 1, 6], [2, 10, 3, 9], [8, 4, 9, 3]]", "knotinfo")
# print(l)
# print(link_components_endpoints(l))
#
# k = from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]", "knotinfo")
# print("Path from", k.nodes["a"][0])
# print(path_from_endpoint(k, k.nodes["a"][0]))
