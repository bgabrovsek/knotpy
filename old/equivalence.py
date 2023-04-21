
# class representing data equivalence class
# add singleten class [data] by self += data or add equivalence data = b


"""
Usage:

data = equivalence([2,3])
data += 1
data[1] = 5
data[2] = 4
data[7] = 6

yields equivalence classes {1,5}, {2,4}, {3}, {6,7}


"""

# TODO: make faster so that no O(n) operations exist

class equivalence:

    def __init__(self, items = []):
        """ items - initial equivalence classes, each element in its own eq. class"""
       # print(items)
        self.classes = []
        self.representative = {}
        for item in items:
            self += item

    # item in eq. class?
    def __contains__(self, item):
        return item in self.representative

    def __iter__(self):
        """Iterate through classes"""
        return iter(self.classes)

    # add element as new eq. class
    def __iadd__(self, item):

        # if adding data list, every element in the list are of equial eq. class
        if isinstance(item, tuple) or isinstance(item, list):
           for i in item:
               self[item[0]] = i

        else:
            if item not in self:
                self.representative[item] = item
                self.classes.append([item])

        return self


    def __len__(self): 
        return len(self.classes)

    # returns representative of item
    def __getitem__(self, item):
        try: return self.representative[item]
        except: raise ValueError("Cannot access item not in list: " + str(item))

    # returns index of class [item]
    def __class_index(self, item):
        for i, l in enumerate(self.classes):
            if item in l: return i
        raise ValueError("Cannot acces class of item: " + str(item))

    # add equivalence item0 = item1 by self[item0] = item1
    def __setitem__(self, item0, item1):

        # add both if not already in
        self += item0
        self += item1

        # item0 and item1 already in the same classes, enough to check if representatives are the same
        if self[item0] == self[item1]: return

        # join [item0] and [item1]

        i0 = self.__class_index(item0)
        i1 = self.__class_index(item1)

        if i0 > i1: i0,i1 = i1,i0

        self.classes[i0] = sorted(self.classes[i0] + self.classes[i1])
        del self.classes[i1]

        # update all to first representative
        for item in self.classes[i0]:
            self.representative[item] = self.classes[i0][0]

        # do not need to sort
        self.classes = sorted(self.classes, key=lambda c: c[0])

    def class_of(self, item):
        return self.classes[self.__class_index(item)]

    def get_classes(self): return self.classes

    def __repr__(self):
        return "{" + ",".join(["[" + ",".join( [str(item) for item in c] ) + "]"  for c in self.classes]) + "}"



"""
data = equivalence([2,3])
data += 1
data[1] = 5
data[2] = 4
data[7] = 6

data+=1
data+=7

data[8] = 8
data+= [7,9,10]

print(data)
print(data.get_classes())"""