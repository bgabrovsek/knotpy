class Vertex(list):
    def __init__(self, data_for_adding):
        adding = data_for_adding
        super(Vertex, self).__init__((1,2,3))
        self.lolz = "vertex"

    def do(self):
        self.lolz = "oh  no"

c = Vertex([1,2,3])
print(c)

#print(min(range(len(data)), key=lambda i: data[i]))

#print(min(data, key=lambda x: list(zip(*x))))