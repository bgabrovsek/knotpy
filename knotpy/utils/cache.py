
class Cache(dict):
    def __init__(self, max_cache_size: int, max_key_length: int):
        """
        A bounded dictionary-based cache that limits:
          - total number of items (max_cache_size)
          - individual item size via len(value) (max_item_length)
        """
        super().__init__()
        self.max_cache_size = max_cache_size
        self.max_key_length = max_key_length

    def __setitem__(self, key, value):
        """
        Store an item in the cache only if:
          - the cache is not full, AND
          - the value's length is within the allowed limit
        """

        key_len = len(key)

        # If the key is too long, do not sture it in the dictionary.
        if key_len > self.max_key_length:
            return

        # If the cache is not full, put the item in the cache.
        if len(self) < self.max_cache_size:
            super().__setitem__(key, value)

        # Cache is full, remove one of the longest elements (we prefer having smaller items in the dictionary)
        else:
            # Store the item only if it is shorter than the max limit (otherwise it is one of the longest).
            if key_len < self.max_key_length and key_len < (max_existing_len := max(len(_) for _ in self)):
                # delete fist biggest item
                for _ in self:
                    if len(_) == max_existing_len:
                        del self[_]
                        break
                super().__setitem__(key, value)
