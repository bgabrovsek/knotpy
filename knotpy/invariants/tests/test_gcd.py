from sympy import symbols, simplify, gcd, fraction


def test1():
    # Define variables
    t1, t2 = symbols('t1 t2')

    # Define the rational expressions
    expressions = [
        (-t1*t2 - t2**2 + t1 + t2)/(t1**2*t2),
        (t1**2 + t1*t2 - t1 - t2)/(t1**2*t2),
        (-t1*t2 - t2**2 + t1 + t2)/(t1**2*t2),
        (t1**2 + t1*t2 - t1 - t2)/(t1**2*t2),
        (t1*t2 + t2**2 - t1 - t2)/(t1*t2**2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1*t2**2),
        (t1*t2 + t2**2 - t1 - t2)/(t1*t2**2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1*t2**2),
        (-t1*t2 - t2**2 + t1 + t2)/(t1*t2**2),
        (t1**2 + t1*t2 - t1 - t2)/(t1*t2**2),
        (-t1*t2 - t2**2 + t1 + t2)/(t1*t2**2),
        (t1**2 + t1*t2 - t1 - t2)/(t1*t2**2),
        (t1*t2 + t2**2 - t1 - t2)/(t1**2*t2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1**2*t2),
        (t1*t2 + t2**2 - t1 - t2)/(t1**2*t2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1**2*t2),
    ]

    # Extract numerators
    numerators = [fraction(expr)[0] for expr in expressions]

    # Compute the GCD of all numerators
    gcd_poly = numerators[0]
    for poly in numerators[1:]:
        gcd_poly = gcd(gcd_poly, poly)

    # Print the result
    print("GCD of numerators:", simplify(gcd_poly))

def test2():
    # Define symbols
    t1, t2 = symbols('t1 t2')

    # Define the rational expressions from the second set
    expressions = [
        -1 / t1 + 1 / (t1 * t2) - t2 / t1 ** 2 + t1 ** (-2),
        1 / t2 + 1 / t1 - 1 / (t1 * t2) - 1 / t1 ** 2,
        - 1 / t1 + 1 / (t1 * t2) - t2 / t1 ** 2 + t1 ** (-2),
        1 / t2 + 1 / t1 - 1 / (t1 * t2) - 1 / t1 ** 2,
        1 / t2 - 1 / t2 ** 2 + 1 / t1 - 1 / (t1 * t2),
        - t1 / t2 ** 2 - 1 / t2 + t2 ** (-2) + 1 / (t1 * t2),
        1 / t2 - 1 / t2 ** 2 + 1 / t1 - 1 / (t1 * t2),
        - t1 / t2 ** 2 - 1 / t2 + t2 ** (-2) + 1 / (t1 * t2),
        - 1 / t2 + t2 ** (-2) - 1 / t1 + 1 / (t1 * t2),
        t1 / t2 ** 2 + 1 / t2 - 1 / t2 ** 2 - 1 / (t1 * t2),
        - 1 / t2 + t2 ** (-2) - 1 / t1 + 1 / (t1 * t2),
        t1 / t2 ** 2 + 1 / t2 - 1 / t2 ** 2 - 1 / (t1 * t2),
        1 / t1 - 1 / (t1 * t2) + t2 / t1 ** 2 - 1 / t1 ** 2,
        - 1 / t2 - 1 / t1 + 1 / (t1 * t2) + t1 ** (-2),
        1 / t1 - 1 / (t1 * t2) + t2 / t1 ** 2 - 1 / t1 ** 2,
        - 1 / t2 - 1 / t1 + 1 / (t1 * t2) + t1 ** (-2)
    ]

    # Extract numerators
    numerators = [fraction(expr)[0] for expr in expressions]

    # Compute GCD of all numerators
    gcd_poly = numerators[0]
    for poly in numerators[1:]:
        gcd_poly = gcd(gcd_poly, poly)

    # Output result
    print("GCD of numerators:", simplify(gcd_poly))

def check_expressions():
    t1, t2 = symbols('t1 t2')

    expressions1 = [
        (-t1*t2 - t2**2 + t1 + t2)/(t1**2*t2),
        (t1**2 + t1*t2 - t1 - t2)/(t1**2*t2),
        (-t1*t2 - t2**2 + t1 + t2)/(t1**2*t2),
        (t1**2 + t1*t2 - t1 - t2)/(t1**2*t2),
        (t1*t2 + t2**2 - t1 - t2)/(t1*t2**2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1*t2**2),
        (t1*t2 + t2**2 - t1 - t2)/(t1*t2**2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1*t2**2),
        (-t1*t2 - t2**2 + t1 + t2)/(t1*t2**2),
        (t1**2 + t1*t2 - t1 - t2)/(t1*t2**2),
        (-t1*t2 - t2**2 + t1 + t2)/(t1*t2**2),
        (t1**2 + t1*t2 - t1 - t2)/(t1*t2**2),
        (t1*t2 + t2**2 - t1 - t2)/(t1**2*t2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1**2*t2),
        (t1*t2 + t2**2 - t1 - t2)/(t1**2*t2),
        (-t1**2 - t1*t2 + t1 + t2)/(t1**2*t2),
    ]

    expressions2 = [
        (-t2 / t1 + 1 / t1) ** 2 * (t1 / t2 - 1 / t2) - t2 / t1 + 1 / t1 + (-t2 / t1 + 1 / t1) / (t1 * t2),
        -(-1 + t1 ** (-2)) / t2 - (-t2 / t1 + 1 / t1) * (t1 / t2 - 1 / t2) / t1,
        -(t2 / t1 - 1 / t1) / t2 + (-t2 / t1 + 1 / t1) / t1,
        (t2 / t1 - 1 / t1) * (-t1 / t2 + 1 / t2) + 1 - 1 / t1 ** 2,
        -(-t2 / t1 + 1 / t1) * (t1 / t2 - 1 / t2) / t2 + 1 / t1 - 1 / (t1 * t2 ** 2),
        (t1 / t2 - 1 / t2) * ((-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) - 1) + (-t1 / t2 + 1 / t2) / (t1 * t2),
        -(-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) + 1 - 1 / t2 ** 2,
        (-t1 / t2 + 1 / t2) / t2 + (-t1 / t2 + 1 / t2) / t1,
        (t2 / t1 - 1 / t1) * (t1 / t2 - 1 / t2) - 1 + t2 ** (-2),
        -(-t1 / t2 + 1 / t2) / t2 + (t1 / t2 - 1 / t2) / t1,
        -((-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) - 1 / (t1 * t2)) / t2 - 1 / t1,
        t1 / t2 + (-t1 / t2 + 1 / t2) * ((-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) - 1 / (t1 * t2)) - 1 / t2,
        -(-t2 / t1 + 1 / t1) / t2 + (t2 / t1 - 1 / t1) / t1,
        (-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) - 1 + t1 ** (-2),
        (-t2 / t1 + 1 / t1) * ((-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) - 1 / (t1 * t2)) + t2 / t1 - 1 / t1,
        -1 / t2 - ((-t2 / t1 + 1 / t1) * (-t1 / t2 + 1 / t2) - 1 / (t1 * t2)) / t1,
    ]

    for x,y in zip(expressions1, expressions2):
        xx = x.subs([(t1, 13), (t2, 7)])
        yy = x.subs([(t1, 13), (t2, 7)])
        print(xx, yy)
        assert xx == yy, "Mismatch in expressions"

    # # tst minors
    # e1 = gcd_of_minors(expressions1, variables=[t1, t2])
    # # tst minors
    # e2 = gcd_of_minors(expressions2, variables=[t1, t2])
    #
    # print("expression 1:", e1)
    # print("expression 1:", e2)

if __name__ == "__main__":
    test1()
    test2()
    check_expressions()