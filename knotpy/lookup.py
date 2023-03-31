def inverse_multi_dict(d):
    """ exchanges keys & vals, but stores keys in a set """
    d_ = dict()  # defaultdict?
    for key, value in d.items():
        if value in d_:
            d_[value].add(key)
        else:
            d_[value] = {key}
    return d_


class Index(dict):
    """General index class."""

    def __init__(self, start=0):
        self.counter = start

    def add(self, old_index):
        return self[old_index]

    def __getitem__(self, old_index):
        if old_index not in self:
            self[old_index] = self.counter
            self.counter += 1
        return super().__getitem__(old_index)

# docstring


def reindex(data, index=None):
    """
    :param data:
    :param index:
    :return:
    """
    if index is None:
        index = Index()  # new index

    if not len(data):
        return type(data)(data)

    if isinstance(data[0], int):
        return type(data)((index[item] for item in data))
    else:
        return type(data)((reindex(item, index) for item in data))


r = Index()
r.add(5)
r.add(4)
r.add(5)
r.add(3)

print(reindex([5, 5, 4, 3], r))
print(reindex([5, 5, 4, 3]))
print(reindex(([4,5,3], [3,3], (4,4,3), [3])))

"""
r = reindex()
print(r[9], r[7], r[3], r[7])"""