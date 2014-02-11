#! /usr/bin/env python

import csv
from broccoli import *

tester = 0 

def term():
	while True:		# infinite loop
		n = raw_input("\n>> ")
		splitLine = n.split()

		if splitLine[0] == "update":
			print "update was typed and recived"  
			do_update(splitLine)

		if splitLine[0] == "setbro":
			print "setbro was typed and recived" 
  			do_setbro(splitLine)
		
		if splitLine[0] == "help":
 			print "help was typed and recived" 
 			do_help(splitLine)

		if splitLine[0] == "list": 
	  		print "list was typed and recived"
	  		do_list(splitLine)

		if splitLine[0] == "setvar": 
			print "setvar was typed and recived"
			do_setvar(splitLine)

		if splitLine[0] == "quit":
			break


def do_setbro(splitLine):
	print "the function is called"
	return
#	# splitLine[1] is a bro script file name
#	# send bro script to bro device
#	# wait for bro script to send list of vars
#	## [(var_name, var_type), ...]
#	## note: in the future, do this as a call back
#	# store vars in dictionary

def do_setvar(splitLine):
	print "the function is called"
	return
#   # splitLine[1] will be var name (e.g., broblemetic_users)
#   # splitLine[2] will be var value (e.g., eric)
#   # if var is an arry, then splitLine will have more vals
#   #   (e.g., eric, alex, oliver)
#   # look up var name in dictionary,
#   # store the value in dictionary
#   # send var name and value to bro device

def do_update(splitLine):
	print "the function is called"
	return
#   # splitLine will not have anything else
#   # send command to bro device to send back
#   #   current values of all vars
#   # store vals in dictionary
#   # call do_list

def do_list(splitLine):
	print "the function is called"
	return
#   # for each var in dictionary,
#   # print varname and value

def do_help(splitLine):
	print ""
	return 
#   # print list of commands and options

term()


# bc = Connection("127.0.0.1:47758") #opens the connection to the bro box 

# @event(addr) #creates the new event to send the addr

# def test1(i):
# 	print i 

# for i in range(len(materials)): 
# 	bc.send("test1",addr(materials[i])) 
# 	#also has IPv6 compatability 
	
# bc.send("test2") 

