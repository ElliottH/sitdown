from __future__ import print_function

import sys

def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def error(*msg):
    sub = ["\n\t%s" % m for m in msg[1:]]
    print(msg[0], *sub, file=sys.stderr)
