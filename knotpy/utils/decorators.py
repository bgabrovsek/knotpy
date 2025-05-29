
def total_ordering_from_compare(cls):
    """Create a class with total order from the cmp method py3_cmp()
    :param cls: decorated class
    :return: self
    """

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    setattr(cls, '__eq__', __eq__)
    setattr(cls, '__ne__', __ne__)
    setattr(cls, '__gt__', __gt__)
    setattr(cls, '__ge__', __ge__)
    setattr(cls, '__lt__', __lt__)
    setattr(cls, '__le__', __le__)

    return cls

