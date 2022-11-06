import copy, collections


class ListBase(collections.MutableSequence):
    def __init__(self, itemType, data=[]):
        self.itemType = itemType
        self._list = list()
        self.extend(list(data))

    ##################################
    # NON-STATIC METHODS
    ##################################
    def check (self, v):
        if self.itemType != None and not isinstance(v, self.itemType):
            import pdb
            pdb.set_trace()
            raise TypeError(v)

    def __eq__(self, other):
        if other is self:
            return True
        if (type(other) != type(self)) or (len(self) != len(other)):
            return False

        return self._list == other._list

    def __add__(self, other):
        assert(type(self) == type(other))
        new = type(self)(self._list)
        new.extend(other)
        return new

    def __iadd__(self, other):
        assert(type(self) == type(other))
        self._list.extend(other._list)
        return self

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __iter__(self):
        for elem in self._list:
            yield elem

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        if isinstance(key, slice):
            new = copy.copy(self)
            new._list = self._list[key]
            return new
        else:
            return self._list[key]

    def __delitem__(self, i):
        del self._list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self._list[i] = v

    def insert(self, i, v):
        self.check(v)
        self._list.insert(i, v)

    def append(self, v):
        self.insert(len(self._list), v)

    def clear(self):
        self._list = list()

    def flatten(self):
        self._list = [item for sublist in self for item in sublist]

    def get_flattened(self):
        new = copy.copy(self)
        new.flatten()
        return new
