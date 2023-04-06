from functools import cached_property
from time import time

class _CachedPropertyReset:
    def __set__(self, obj, value):
        d = obj.__dict__
        d["data"] = value
        if not obj.hold:
            if "sum" in d:
                del d["sum"]

class myclass_cached:

    data = _CachedPropertyReset()
    def __init__(self, n):
        self.data = list(range(n))
        self.hold = False

    def work_on_data(self):
        self.data = [d+1 for d in self.data]

    @cached_property
    def sum(self):
        return sum(self.data)


class myclass_not_cached:

    def __init__(self, n):
        self.data = list(range(n))

    def work_on_data(self):
        self.data = [d+1 for d in self.data]


    def sum(self):
        return sum(self.data)


time0 = time()


c = myclass_not_cached(25)
for j in range(10000000):
    c.work_on_data()
print(c.sum())


time1 = time()

c = myclass_cached(25)
for j in range(10000000):
    c.work_on_data()
print(c.sum)

time2 = time()


print(time1-time0, time2-time1)


"""
x = myclass(5)
print(x.sq())
print(x.sqc)
print(x.sqc)
"""