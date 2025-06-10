from knotpy.utils.parsing import universal_list_of_lists_parser

def test_universal_list_of_lists_parser():
    # Test examples
    examples = [
        "[[1,2,3],[4,5,0],[1,3,5,8]]",
        "(1,2,3),(4,5,0),(1,3,5,8)",
        "1 2 3, 4 5 0, 1 3 5 8",
    ]

    truth = [[1,2,3],[4,5,0],[1,3,5,8]]



    for ex in examples:

        result = universal_list_of_lists_parser(ex)
        print(result)

        assert universal_list_of_lists_parser(ex) == truth, "Failed for example {}".format(ex)

if __name__ == '__main__':
    test_universal_list_of_lists_parser()