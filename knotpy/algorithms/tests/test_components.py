
import pytest

import knotpy as kp

class TestComponents:

    def setup_method(self):
        pass

    def test_knot(self):
        trefoil = kp.from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]", "knotinfo")
        assert len(list(kp.faces(trefoil))) == 5



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
