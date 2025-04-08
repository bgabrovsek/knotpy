from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.components_link import number_of_link_components

def test_number_of_link_components():
    pd_K_3_1 = "X[1,5,2,4], X[3,1,4,6], X[5,3,6,2]"
    pd_K_8_13 = "X[1,9,2,8],X[3,14,4,15],X[5,12,6,13],X[7,11,8,10],X[9,3,10,2],X[11,16,12,1],X[13,4,14,5],X[15,6,16,7]"
    pd_L2a1 = "X[4, 1, 3, 2], X[2, 3, 1, 4]" # hopf
    pd_L6a2 = "X[8, 1, 9, 2], X[12, 5, 7, 6], X[10, 3, 11, 4], X[4, 11, 5, 12], X[2, 7, 3, 8], X[6, 9, 1, 10]"
    pd_L6a5 = "X[6, 1, 7, 2], X[10, 3, 11, 4], X[12, 7, 9, 8], X[8, 11, 5, 12], X[2, 5, 3, 6], X[4, 9, 1, 10]"

    K_3_1 = from_pd_notation(pd_K_3_1)
    K_8_13 = from_pd_notation(pd_K_8_13)
    L2a1 = from_pd_notation(pd_L2a1)
    L6a2 = from_pd_notation(pd_L6a2)
    L6a5 = from_pd_notation(pd_L6a5)

    assert number_of_link_components(K_3_1) == 1
    assert number_of_link_components(K_8_13) == 1
    assert number_of_link_components(L2a1) == 2
    assert number_of_link_components(L6a2) == 2
    assert number_of_link_components(L6a5) == 3

if __name__ == '__main__':
    test_number_of_link_components()