from knotpy.classes.planardiagram import PlanarDiagram
from copy import deepcopy

def mirror(k: PlanarDiagram) -> PlanarDiagram:
    if not k.is_knotted:
        return k  # deepcopy?
    mirror_k = deepcopy(k)
    for node in mirror_k.nodes:
        node.mirror()
    return mirror_k
