#! /usr/bin/env python

import time as Time
from broccoli import *

bc = Connection("127.0.0.1:47758") 

@event
def test2(a,b,c,d,e,f,g,h,i,j,i6,j6):
    global recv
    recv += 1
    print "==== atomic a %d ====" % recv
    print repr(a), a
    print repr(b), b
    print "%.4f" % c
    print d
    print repr(e), e
    print f
    print repr(g), g
    print repr(h), h
    print repr(i), i
    print repr(j), j
    print repr(i6), i6
    print repr(j6), j6

test2

bc.processInput();
 