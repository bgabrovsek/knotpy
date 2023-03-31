from copy import deepcopy


class InvariantBucket:

    def __init__(self, f_invariant):
        self.pairs = []
        self.f_invaraint = f_invariant

    def add(self, knot):
        knot_invariant = self.f_invaraint(knot)
        for (key, L) in self.pairs:
            if knot_invariant == key:
                if knot not in L:
                    L.append(knot)
                    return True
                else:
                    return False

        # not found
        self.pairs.append((knot_invariant, [knot]))
        return True

    def __len__(self):
        return len(self.pairs)

    def number_of_values(self):
        return sum([len(L) for key, L in self.pairs])

    def keys(self):
        return [key for key, T in self.pairs]

    def __getitem__(self, key):
        for (key_, L) in self.pairs:
            if key_ == key:
                return L
        return []

    def __repr__(self):
        s = len(self.values) + "keys and " + self.number_of_values() + " values."