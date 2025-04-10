from knotpy.notation.plantri import from_plantri_notation, to_plantri_notation
from knotpy.algorithms.sanity import sanity_check
def test_from_plantri():
    plantris = [
        ["5 bcde,aedc,abd,acbe,adb", "bcde, aedc, abd,acbe,adb "],
        ["7: 1[2 3 4 5] 2[1 5 6 3] 3[1 2 6 4] 4[1 3 6 5] 5[1 4 6 2] 6[2 5 4 3]",
        "1[2  3  4  5] 2[1    5  6  3]   3[1  2  6  4]   4[1  3  6  5] 5[1  4  6  2] 6[2  5  4  3]"],
        ["5 bccd,adee,aaed,aceb,bbdc", "bccd,adee,aaed,aceb,bbdc"]  # example from Wanda
    ]

    for plantri1, plantri2 in plantris:
        k1 = from_plantri_notation(plantri1)
        k2 = from_plantri_notation(plantri2)

        assert sanity_check(k1)
        assert sanity_check(k2)

        assert k1 == k2



if __name__ == '__main__':
    test_from_plantri()
