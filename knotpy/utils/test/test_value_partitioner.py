from knotpy.utils.dict_utils import ClassifierDict

def mod2(a):
    """Mod 2.
    
    Args:
        a: The a parameter.
    
    Returns:
        The return value.
    """
    return a % 2

def mod3(a):
    """Mod 3.
    
    Args:
        a: The a parameter.
    
    Returns:
        The return value.
    """
    return a % 3

def test_value_partitioner():

    """Test value partitioner.
    """
    v = ClassifierDict({"mod2": mod2, "mod3": mod3})

    for i in range(18):
        v.append(i)

    assert sorted(v.values()) == [[0, 6, 12], [1, 7, 13], [2, 8, 14], [3, 9, 15], [4, 10, 16], [5, 11, 17]]
    assert sorted(v.keys()) == [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]


if __name__ == '__main__':
    test_value_partitioner()
