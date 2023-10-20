"""Algorithms with orientation."""
from knotpy.classes.planardiagram import PlanarDiagram


def oriented(k: PlanarDiagram) -> PlanarDiagram:

    ok = k.to_oriented_class()
    print(ok)
    pass


from knotpy.generate.example import trefoil_knot
k = trefoil_knot()
oriented(k)

print(k)