from knotpy.tables.name import clean_name, parse_name
def test_clean_name():
    assert clean_name("3_1") == "3_1"
    assert clean_name("trefoil") == "3_1"
    assert clean_name("31") == "3_1"
    assert clean_name("112") == "11_2"
    assert clean_name("K10_14") == "10_14"
    assert clean_name("11a17") == "11a_17"
    assert clean_name("L6a2") == "L6a_2"
    assert clean_name("l6A2") == "L6a_2"
    assert clean_name("T31") == "T3_1"
    assert clean_name("H31") == "H3_1"
    assert clean_name("*3_1") == "3_1*"
    assert clean_name("3_1*") == "3_1*"
    assert clean_name("+3_1") == "3_1+"
    assert clean_name("-3_1") == "3_1-"
    assert clean_name("**k3_1") == "3_1"
    assert clean_name("-t3_1") == "T3_1-"
    assert clean_name("-*t3_1") == "T3_1*-"
    assert clean_name("*-t3_1") == "T3_1*-"
    assert clean_name("-t3_1*") == "T3_1*-"
    assert clean_name("*t3_1-") == "T3_1*-"
    assert clean_name("t3_1--*") == "T3_1*--"
    assert clean_name("3_1+-") == "3_1+-"
    assert clean_name("3_1{+-}") == "3_1+-"
    assert clean_name("3_1(+,-,+)") == "3_1+-+"
    assert clean_name(" L6a_2 {+,-,+,+,-} * ") == "L6a_2*+-++-"

def test_parse_name():
    # (type, crossing number, alt/nalt/None, index, mirror, orientation)
    assert parse_name("3_1") == ("knot", 3, None, 1, False, "")
    assert parse_name("11a_5") == ("knot", 11, "a", 5, False, "")
    assert parse_name("11n_7*") == ("knot", 11, "n", 7, True, "")
    assert parse_name("L6a_2") == ("link", 6, "a", 2, False, "")
    assert parse_name("L6n_3*+-") == ("link", 6, "n", 3, True, "+-")
    assert parse_name("T3_1++-") == ("theta", 3, None, 1, False, "++-")
    assert parse_name("H4_2*--++") == ("handcuff", 4, None, 2, True, "--++")
    assert parse_name("L6a_2*") == ("link", 6, "a", 2, True, "")
    assert parse_name("H0_1") == ("handcuff", 0, None, 1, False, "")
    assert parse_name("T0_1") == ("theta", 0, None, 1, False, "")

if __name__ == "__main__":
    # Run test
    test_clean_name()
    test_parse_name()