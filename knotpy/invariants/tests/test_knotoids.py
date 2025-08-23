import knotpy as kp
from knotpy import export_pdf


def test_affine_index_polynomial():
    kp.settings.allowed_moves = "r1,r2,r3"
    k = kp.from_pd_notation("X[0,4,1,5],X[5,1,6,2],X[2,6,3,7],X[8,4,7,3],V[0],V[8]")

    p = kp.affine_index_polynomial(k)

    i = 0
    for k_ in kp.all_reidemeister_moves(k, depth=2):
        if (i := i+1)% 2:
            continue
        p_ = kp.affine_index_polynomial(k_)
        assert p == p_, f"{k} \n{p}\n{p_}"

    # for k_ in kp.all_orientations(k):
    #     p_ = kp.affine_index_polynomial(k_)
    #     assert p == p_, f"{k} \n{p}\n{p_} (orientations)"


def test_arrow_polynomial():
    kp.settings.allowed_moves = "r1,r2,r3"
    k = kp.from_pd_notation("X[0,4,1,5],X[5,1,6,2],X[2,6,3,7],X[8,4,7,3],V[0],V[8]")
    #export_pdf(k, "knotoids.pdf")

    p = kp.arrow_polynomial(k)

    for k_ in kp.all_reidemeister_moves(k, depth=1):
        p_ = kp.arrow_polynomial(k_)
        #export_pdf([k, k_], "knotoids_moves.pdf")
        assert p == p_, f"{k} \n{p}\n{p_}"

    for k_ in kp.orientations(k):
        p_ = kp.arrow_polynomial(k_)
        assert p == p_, f"{k} \n{p}\n{p_} (orientation)"


def test_mock_polynomial():
    kp.settings.allowed_moves = "r1,r2,r3"
    k = kp.from_pd_notation("X[0,4,1,5],X[5,1,6,2],X[2,6,3,7],X[8,4,7,3],V[0],V[8]")
    #export_pdf(k, "knotoids.pdf")

    p = kp.mock_alexander_polynomial(k)

    for k_ in kp.all_reidemeister_moves(k, depth=1):
        p_ = kp.mock_alexander_polynomial(k_)
        #export_pdf([k, k_], "knotoids_moves.pdf")
        assert p == p_, f"{k} \n{p}\n{p_}"

    for k_ in kp.orientations(k):
        p_ = kp.mock_alexander_polynomial(k_)
        assert p == p_, f"{k} \n{p}\n{p_} (orientation)"



def test_kauffman_polynomial():
    kp.settings.allowed_moves = "r1,r2,r3"
    k = kp.from_pd_notation("X[0,4,1,5],X[5,1,6,2],X[2,6,3,7],X[8,4,7,3],V[0],V[8]")
    #export_pdf(k, "knotoids.pdf")

    p = kp.kauffman_bracket_skein_module(k, normalize=True)

    for k_ in kp.all_reidemeister_moves(k, depth=1):
        p_ = kp.kauffman_bracket_skein_module(k_, normalize=True)
        #export_pdf([k, k_], "knotoids_moves.pdf")
        assert p == p_, f"{k} \n{p}\n{p_}"

    for o in kp.orientations(k):
        p_ = kp.kauffman_bracket_skein_module(k_, normalize=True)
        assert p == p_, f"{k} \n{p}\n{p_} (orientation)"

def test_yamada_polynomial():

    k = kp.from_pd_notation("X[0,4,1,5],X[5,1,6,2],X[2,6,3,7],X[8,4,7,3],V[0],V[8]")
    #export_pdf(k, "knotoids.pdf")

    p = kp.yamada(kp.closure(k, over=True, under=True))

    for i,k_ in enumerate(kp.all_reidemeister_moves(k, depth=1)):
        if i%15:
            continue

        p_ = kp.yamada(kp.closure(k_, True, True))
        #export_pdf([k, k_], "knotoids_moves.pdf")
        assert p == p_, f"{k} \n{p}\n{p_}"

    # for o in kp.all_orientations(k):
    #     p_ = kp.yamada(kp.closure(k, True, True))
    #     assert p == p_, f"{k} \n{p}\n{p_} (orientation)"

if __name__ == '__main__':

    test_arrow_polynomial()
    test_affine_index_polynomial()
    test_mock_polynomial()
    test_kauffman_polynomial()
    test_yamada_polynomial()