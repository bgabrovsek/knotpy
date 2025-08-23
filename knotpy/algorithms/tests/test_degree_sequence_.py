from knotpy.algorithms.degree_sequence import degree_sequence, neighbour_sequence
from knotpy.notation.native import from_knotpy_notation


def test_deg_seq():
    #pd_8_3 = "X(6,2,7,1),X(14,10,15,9),X(10,5,11,6),X(12,3,13,4),X(4,11,5,12),X(2,13,3,14),X(16,8,1,7),X(8,16,9,15)"
    pd_8_3 = "a=X(c3 f0 g3 g2) b=X(f3 c0 h3 h2) c=X(b1 e2 e1 a0) d=X(e3 f2 f1 e0) e=X(d3 c2 c1 d0) f=X(a1 d2 d1 b0) g=X(h1 h0 a3 a2) h=X(g1 g0 b3 b2)"
    k = from_knotpy_notation(pd_8_3)

    assert degree_sequence(k) == (4, )* 8


    assert neighbour_sequence(k, "a") == (1, 3, 4)
    assert neighbour_sequence(k, "h") == (1, 2, 3, 2)


if __name__ == '__main__':
    test_deg_seq()
