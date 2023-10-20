
class a:
    def x(self):
        print("type a")

class b(a):
    def x(self):
        print("type b")


x = a()
y = b()

print("x is a", isinstance(x, a))
print("x is b", isinstance(x, b))
print("y is a", isinstance(y, a))
print("y is b", isinstance(y, b))
print("x is", type(x))
print("y is", type(y))
print("x is a", type(x) is a)
print("x is b", type(x) is b)
print("y is a", type(y) is a)
print("y is b", type(y) is b)
print("a is type", type(a) is type)
print("b is type", type(b) is type)
