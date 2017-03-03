from sys import maxsize
from math import floor, ceil

def splitItems(aitem, bitem):
    if isinstance(aitem, tuple):
        atuple = aitem[1]
        aval = aitem[0]
    else:
        atuple = maxsize
        aval = aitem

    if isinstance(bitem, tuple):
        btuple = bitem[1]
        bval = bitem[0]
    else:
        btuple = maxsize
        bval = bitem

    return (aval, bval, atuple, btuple)

class skiplist():
    def __init__(self, items=[]):
        # We assume the list is already sorted, we don't want the overhead of
        # sorting, or checking if it's sorted
        self.items = items
        stride = self.stride()
        for i in range(0, len(items), self.stride()):
            if i + stride < len(self.items):
                next = self.items[i + stride]
            else:
                next = self.items[-1] + 1
            self.items[i] = (self.items[i], next)

    def stride(self):
        list_length = len(self.items)
        count = self.count()
        if count != 0:
            return ceil(list_length / count)
        else:
            return 1

    def count(self):
        return floor(len(self.items)**0.5)

    def values(self):
        for val in self.items:
            if isinstance(val, tuple):
                yield val[0]
            else:
                yield val

    def __iter__(self):
        return self.values()

    def __repr__(self):
        return "skiplist(%s)" % str(self.items)

    def __len__(self):
        return len(self.items)

    def __or__(self, other):
        # Skip lists don't really buy us anything here...
        out = []

        # list cursors
        a = 0
        b = 0

        while a < len(self.items) and b < len(other.items):
            aval, bval, a_skip, b_skip = splitItems(self.items[a], other.items[b])
            if aval == bval:
                out.append(aval)
                a += 1
                b += 1
            elif aval < bval:
                out.append(aval)
                a += 1
            else:
                out.append(bval)
                b += 1

        for val in self.items[a:]:
            if isinstance(val, tuple):
                out.append(val[0])
            else:
                out.append(val)

        for val in other.items[b:]:
            if isinstance(val, tuple):
                out.append(val[0])
            else:
                out.append(val)

        return skiplist(out)

    def __and__(self, other):
        # There are 5 cases we must consider at each step
        # 1) Taking the skip pointer for a
        # 2) Taking the skip pointer for b
        # 3) Adding the item to the output and incrementing a and b
        #    since self.items[a] == other.items[b]
        # 4) Increment a since self.items[a] < other.items[b]
        # 5) Increment b since self.items[a] > other.items[b]

        out = []

        # list cursors
        a = 0
        b = 0

        # Store stride values rather than recalculating
        astride = self.stride()
        bstride = other.stride()

        while a < len(self.items) and b < len(other.items):
            # Returned skip values are a very large value if this is not a skip pointer
            # This reduces the number of cases that we must test
            aval, bval, a_skip, b_skip = splitItems(self.items[a], other.items[b])

            if a_skip <= bval:
                # We can take the skip pointer for a
                a += astride
            elif b_skip <= aval:
                # We can take the skip pointer for b
                b += bstride

            # We can't take the skip pointers, so do a normal merge
            elif aval == bval:
                out.append(aval)
                a += 1
                b += 1
            elif aval < bval:
                a += 1
            else: # aval > bval
                b += 1

        return skiplist(out)

    def __sub__(corpus, self):
        other = corpus
        # Skip lists don't really buy us anything here...
        out = []

        # list cursors
        a = 0 # this list
        b = 0 # entire list of documents

        while a < len(self.items) and b < len(other.items):
            aval, bval, a_skip, b_skip = splitItems(self.items[a], other.items[b])
            if aval == bval:
                a += 1
                b += 1
            elif aval < bval:
                a += 1
            else:
                out.append(bval)
                b += 1

        # Add anything left in the corpus
        for val in other.items[b:]:
            if isinstance(val, tuple):
                out.append(val[0])
            else:
                out.append(val)

        return skiplist(out)

