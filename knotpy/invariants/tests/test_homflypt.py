import knotpy as kp

def test_homflypt():
    for knot_name, invariants in kp.get_knot_table_invariants([0,8]).items():
        real_h = invariants['homflypt']

        d = invariants['diagram']

        h = kp.homflypt_polynomial(d)
        h_ = kp.homflypt_polynomial(kp.mirror(d))

        print(knot_name, "OK" if h == real_h else "NOT OK")
        print("real", real_h)
        print("   h", h)
        print("mirh", h_)

        #assert real_h == h

    pass

if __name__ == '__main__':

    k = kp.PlanarDiagram("3_1")
    kp.draw(k)
    kp.plt.show()
    test_homflypt()

    """
    -v**4 + v**2*z**2 + 2*v**2 vs 
    z**2/v**2 + 2/v**2 - 1/v**4
       
    """