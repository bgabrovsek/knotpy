class NumberGenerator:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.limit:
            result = self.current
            self.current += 1
            return result
        else:
            raise StopIteration

# Example usage
limit = 5
number_iterator = NumberGenerator(limit)

for num in number_iterator:
    print(num)

print(list(NumberGenerator(10)))