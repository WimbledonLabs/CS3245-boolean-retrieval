from skiplist import skiplist
from random import randint
import operator

MAX_LENGTH = 10000
MAXINT = 10000

def uniq_sorted(a):
    return sorted(list(set(a)))

def testOp(op):
    for i in range(1000):
        src_length = randint(0, MAX_LENGTH)

        val_min = randint(0, MAXINT)
        val_max = randint(0, MAXINT)
        val_min, val_max = tuple(sorted([val_min, val_max]))

        a = uniq_sorted( [randint(0, MAXINT) for x in range(src_length)] )


        src_length = randint(0, MAX_LENGTH)

        val_min = randint(0, MAXINT)
        val_max = randint(0, MAXINT)
        val_min, val_max = tuple(sorted([val_min, val_max]))

        b = uniq_sorted( [randint(0, MAXINT) for x in range(src_length)] )


        # Do set first since the skip list modifies the list
        set_res  = sorted(list(      op(set(a), set(b))       ))
        skip_res = sorted(list( op(skiplist(a), skiplist(b))  ))
        assert skip_res == set_res

testOp(operator.__and__)
testOp(operator.__or__)
