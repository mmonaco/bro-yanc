#! /usr/bin/env python

import time as Time

from broccoli import *

@event
def test2(a,b,c,d,e,f,g,h,i,j,i6,j6):
    global recv #the reciever counter
    recv += 1 # it adds one to mention one test 
    print "\n"
    print "On the python end: \n" 
    print repr(a) #the other end 
    print repr(b) 
    print repr(e) 
    print repr(g) 
    print repr(h) 
    print repr(i) 
    print repr(j) 
    print repr(i6) 
    print repr(j6)
    
bc = Connection("127.0.0.1:47758") 
#makes the connection 

bc.send("test1") 
#initiate test1, which will send back to the python script from the bro

recv = 0 
#reciever counter is set to 0
while True:
    bc.processInput();
     #wait for the input
    if recv == 1: 
    #this is the number of recieving data grams it is looking for. 2 for 2 tests
        break
    Time.sleep(1)

