__all__ = ["EquivalenceRelation"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

if __name__ == "__main__":
    # four equivalent classes
    e = EquivalenceRelation([0,1,2])
    e += 3
    e += 4

    e[0] = 0
    e[0] = 3  # join classes 0 and 3
    e[3] = 3
    e[5] = 5
    e[3] = 4  # join classes 4 and 3
    e[1] = 2
    print(list(e.classes()))
    print(list(min(c) for c in e.classes()))
    print(list(e.representatives()))
    print(list(e))


"""

[{0}, {1}, {2}, {3}, {4}]
[{0, 3}, {1}, {2}, {4}]
[{0, 3, 4}, {1}, {2}]
[{0, 3, 4}, {1, 2}]

[{0}, {1}, {2}, {3}, {4}]
[{0, 3}, {1}, {2}, {4}, {5}]
[{0, 3, 4}, {1}, {2}, {5}]
[{0, 3, 4}, {1, 2}, {5}]

"""