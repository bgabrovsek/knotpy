class Vertex(list):
    def __init__(self, data):
        super(Vertex, self).__init__(data)
        self.name = "vertex"

c = Vertex([1,2,3])
print(c)

#print(min(range(len(data)), key=lambda i: data[i]))

#print(min(data, key=lambda x: list(zip(*x))))