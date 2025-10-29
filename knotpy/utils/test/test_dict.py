import knotpy as kp
def test_dict():
    """Test dict.
    """
    d = {
        'a': {1, 2},
        'b': {2, 3},
        'c': {1}
    }
    print(kp.utils.dict_utils.invert_dict_of_sets(d))

if __name__ == "__main__":
    test_dict()
