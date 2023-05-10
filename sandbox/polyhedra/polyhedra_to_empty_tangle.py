import knotpy as kp
import string
from glob import glob
from pathlib import Path

data_dir = Path("/Users/bostjan/Dropbox/Code/knotpy/sandbox/polyhedra/data")

def graph_to_empy_tangle(g):

    compass = {0:"NE", 1:"NW", 2:"SW", 3:"SE"}
    verts = ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"]




    n3 = [v for v in g.nodes if g.degree(v) == 3]  # nodes of degree 3
    n4 = [v for v in g.nodes if g.degree(v) == 4]  # nodes of degree 3



    to_connect = []

    for (v, vp), (u, up) in g.arcs():

        if v in n3 and u in n4:
            (v, vp), (u, up) = (u, up), (v, vp)

        cn = []

        for w, wp in [(v, vp), (u, up)]:
            cn += [n4.index(w), compass[wp]] if w in n4 else ["v" + str(n3.index(w)+1)]

        to_connect.append(tuple(cn))



    return "".join(str(to_connect).split())


g = kp.from_plantri_notation("bcde,aedc,abd,acbe,adb")
t = graph_to_empy_tangle(g)


for fn in glob(str(data_dir / "poly*")):

    print(fn)


    graphs = kp.loadtxt_multiple(fn,notation="plantri",ccw=True,separator=",")


    empty = [graph_to_empy_tangle(g) for g in graphs]

    f = open(fn.replace("poly-", "tang-"), mode="wb")

    f.write(f"# {len(empty)} polyhedra\n".encode("utf-8"))

    for e in empty:
        f.write((e + "\n").encode("utf-8"))

    f.close()
    for g, e in zip(graphs, empty):
        print(e)


#g = kp.from_plantri_notation("bcde,aedc,abd,acbe,adb")
#graph_to_empy_tangle(g)

# tangle format
"""
def H41(a,b,c,d):
    clear()
    a,b,c,d = create([a,b,c,d]) 
    reflect([b,d])
    v1,v2 = vertices3(2)
    to_connect = [(a,'NE',v2),(a,'SE',c,'NE'),(a,'SW',b,'SW'),(a,'NW',v1),
                  (b,'NE',d,'SE'),(b,'SE',v1),(b,'NW',c,'NW'),
                  (c,'SE',v2),(c,'SW',d,'SW'),
                  (d,'NE',v1),(d,'NW',v2)]
    connect(to_connect)
    direct()
    pd = PDcode()
    return pd


"""

