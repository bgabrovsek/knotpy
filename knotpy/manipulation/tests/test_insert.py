from knotpy.notation.native import from_knotpy_notation
from knotpy.manipulation.insert import insert_endpoint

def test_insert_attr():
    k = from_knotpy_notation("a=V(b0 a2 a1 c0) b=V(a0) c=V(a3)")
    k.add_vertex("f", degree=1)
    k.nodes["a"]._inc[1].attr = {"color":1}
    k.nodes["a"]._inc[2].attr = {"color":1}

    print(k)
    insert_endpoint(k, ("a", 0), None)
    print(k)


if __name__ == '__main__':
    test_insert_attr()