#! /usr/bin/env python

import time as Time

from broccoli import *

@event
def update(a,b):
    global recv #the reciever counter
    recv += 1 # it adds one to mention one init_update
    print "\n"
    print "On the python end: \n" 
    print repr(a) #the other end 
    print repr(b) 
    
bc = Connection("127.0.0.1:47758") 
#makes the connection 

bc.send("init_update") 
#initiate init_update, which will send back to the python script from the bro

recv = 0 
#reciever counter is set to 0
while True:
    bc.processInput();
     #wait for the input
    if recv == 1: 
    #this is the number of recieving data grams it is looking for. 2 for 2 init_update
        break
    Time.sleep(1)

