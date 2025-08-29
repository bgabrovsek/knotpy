import knotpy as kp
from time import time

def test_homflypt():

    # unoriented
    for k in kp.knots(range(0, 8), mirror=True, oriented=False):
        kp.settings.use_precomputed_invariants = False
        h = kp.homflypt(k, variables="xyz")
        kp.settings.use_precomputed_invariants = True
        h_p = kp.homflypt(k, variables="xyz")
        assert h == h_p

    # oriented
    for k in kp.knots(range(0, 8), mirror=True, oriented=True):
        kp.settings.use_precomputed_invariants = False
        h = kp.homflypt(k, variables="xyz")
        kp.settings.use_precomputed_invariants = True
        h_p = kp.homflypt(k, variables="xyz")
        assert h == h_p

    kp.settings.use_precomputed_invariants = True


def test_precomputed_speed():

    N = 12

    kp.settings.use_precomputed_invariants = False

    t = time()
    for k in kp.knots(range(0, N), mirror=True, oriented=False):
        kp.homflypt(k, variables="xyz")
    t_non_precomputed = time() - t

    kp.settings.use_precomputed_invariants = True

    t = time()
    for k in kp.knots(range(0, N), mirror=True, oriented=False):
        kp.homflypt(k, variables="xyz")
    t_precomputed = time() - t

    print("Non-precomputed:", t_non_precomputed)
    print("    Precomputed:", t_precomputed)

if __name__ == '__main__':
    test_homflypt()
    test_precomputed_speed()