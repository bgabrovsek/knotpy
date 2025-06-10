import knotpy as kp
def test_flype():
    for k in kp.knots((4, 8)):
        print(k)
        h = kp.homflypt_polynomial(k)
        for f in kp.find_flype(k):
            print(f)
            fk = kp.flype(k, f)
            assert kp.sanity_check(fk)
            fh = kp.homflypt_polynomial(fk)
            assert h == fh

            assert k != fk
            #print(kp.canonical(k) != kp.canonical(fk))

    #kp.export_pdf(kp.knot("8_19"), "lala.pdf", with_labels=True)

def test_flype_case():
    k = kp.knot("6_2")



    for i, f in enumerate(kp.find_flype(k)):

        print(f)
        fk = kp.flype(k, f)
        print(fk)
        assert kp.sanity_check(fk)

if __name__ == '__main__':
    test_flype()