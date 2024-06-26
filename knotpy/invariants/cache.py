class Cache:
    def __init__(self, max_number_of_nodes, cache_size=None):
        self.cache_size = cache_size
        self.cache = dict()
        self.usage_count = dict()
        self.max_number_of_nodes = max_number_of_nodes

    def get(self, key):
        if key in self.cache:
            self.usage_count[key] += 1
            return self.cache[key]
        return None

    def set(self, key, value):
        if len(key) <= self.max_number_of_nodes:
            if key in self.cache:
                self.cache[key] = value
                self.usage_count[key] += 1
            else:
                if self.cache_size and len(self.cache) >= self.cache_size:
                    # Find the least frequently used item
                    least_frequent_key = min(self.usage_count, key=self.usage_count.get)
                    del self.cache[least_frequent_key]
                    del self.usage_count[least_frequent_key]
                self.cache[key] = value
                self.usage_count[key] = 1
