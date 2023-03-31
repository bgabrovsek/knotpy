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

x = myclass(5)
print(x.sq())
print(x.sqc)
print(x.sqc)