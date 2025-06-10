import numpy as np

from knotpy.classes.planardiagram import PlanarDiagram


def tutte_layout(k:PlanarDiagram):

    faces = sorted(k.faces, key=len)
    outer_face = faces[-1]

    
    

if __name__ == "__main__":
    k = PlanarDiagram("5_2")
    tutte_layout(k)
    print("lol")