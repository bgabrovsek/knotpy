from string import ascii_letters

from knotpy.classes.tangle import Tangle


def vertical_tangle(create_using=None):

    if create_using is not None and type(create_using) is not type:
        raise TypeError("Creating tangle with create_using instance not yet supported.")

    t = Tangle(name="\u221E")
    t.add_terminals_from(["NE", "SE", "NW", "SW"])
    t.set_arc([("NE", 0), ("SE", 0)])
    t.set_arc([("SW", 0), ("NW", 0)])
    return t


def horizontal_tangle(create_using=None):
    t = Tangle(name="0")
    t.add_terminals_from(["NE", "SE", "NW", "SW"])
    t.set_arc([("NE", 0), ("NW", 0)])
    t.set_arc([("SW", 0), ("SE", 0)])
    return t


def integer_tangle(n: int, create_using=None):
    t = Tangle(name=str(n))
    if n == 0:
        return vertical_tangle(create_using=create_using)

    crossings = ascii_letters[:abs(n)]

    t.add_terminals_from(["NE", "SE", "NW", "SW"])
    t.add_crossings_from(crossings)

    if n > 0:
        t.set_arc([("NW", 0), (crossings[0], 3)])
        t.set_arc([("SW", 0), (crossings[0], 0)])
        t.set_arc([("NE", 0), (crossings[-1], 2)])
        t.set_arc([("SE", 0), (crossings[-1], 1)])
        for a, b in zip(ascii_letters[:abs(n) - 1], ascii_letters[1:abs(n)]):
            t.set_arc([(a, 2), (b, 3)])
            t.set_arc([(a, 1), (b, 0)])
    else:
        t.set_arc([("NW", 0), (crossings[0], 0)])
        t.set_arc([("SW", 0), (crossings[0], 1)])
        t.set_arc([("NE", 0), (crossings[-1], 3)])
        t.set_arc([("SE", 0), (crossings[-1], 2)])
        for a, b in zip(ascii_letters[:abs(n) - 1], ascii_letters[1:abs(n)]):
            t.set_arc([(a, 3), (b, 0)])
            t.set_arc([(a, 2), (b, 1)])

    return t


if __name__ == "__main__":

    from knotpy.notation.plantri import from_plantri_notation

    print(horizontal_tangle())
    print(vertical_tangle())
    print(integer_tangle(3))
