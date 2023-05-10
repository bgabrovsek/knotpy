from random import choice
import random
from datetime import datetime

class filt():

    def __init__(self, x):
        self.x = x

    def __iter__(self):
        self.iter = iter(self.x)
        return self

    def __next__(self):
        while True:
            ne = next(self.iter)
            print("next", ne )
            if ne % 5:
                return ne

    def __len__(self):
        return len(list(item for item in self.x if item % 5))

    def __getitem__(self, item):
        print("item", item)
        return self.x[item]

    def __bool__(self):
        try:
            _ = next(iter(self))
        except StopIteration:
            return False
        return True





a = {99:2,5:6, 8:9, 10:11, 19:20}


b = filt(a)
c = filt({5:6})

print(bool(b))
print(bool(c))
random.seed(datetime.now().timestamp())

print("choice", choice(b))
#for x in b:
#    print(x)
