from functools import cached_property

class myclass:
    def __init__(self, n):
        self.n = n

    def sq(self):
        print("computing")
        return self.n*self.n

    @cached_property
    def sqc(self):
        print("computing (cached)")
        return self.n*self.n


class vsota1:
    def __init__(self, data):
        self.data = data
    @property
    def sum(self):
        return sum(self.data)


class _CachedPropertyResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["data"] = value
        if "sum" in od:
            del od["sum"]

        print("set")

    def __setitem__(self, obj, key, value):
        od = obj.__dict__
        od["data"][key] = value
        if "sum" in od:
            del od["sum"]

        print("setitem")

class vsota2:

    data = _CachedPropertyResetter()
    def __init__(self, data):
        self.data.update(data)

    @cached_property
    def sum(self):
        return sum(self.data)

def test(f):
    a = f([1,2,3])
    s = 0
    print(".")
    for i in range(50):
        a.data[0] = i
        s += a.sum
    return s


print(test(vsota1))
print(test(vsota2))

"""
x = myclass(5)
print(x.sq())
print(x.sqc)
print(x.sqc)
"""