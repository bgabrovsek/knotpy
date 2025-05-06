from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.invariants.jones_polynomial import jones_polynomial
from knotpy.reidemeister.reidemeister import randomize_diagram

def test_randomize():

    k = PlanarDiagram("3_1")
    j = jones_polynomial(k)

    for i in range(10):
        k_ = randomize_diagram(k, crossing_increasing_moves=2)
        assert k != k_  # unlikely they are the same
        assert jones_polynomial(k_) == j
        print(k_)

if __name__ == '__main__':
    test_randomize()