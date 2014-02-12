#! /usr/bin/env python

from broccoli import *

bc = Connection("127.0.0.1:47758")

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

user_dict ={}

def do_setbro(splitLine):
	print "the function is called"
#	# splitLine[1] is a bro script file name
#	# send bro script to bro device
#	# wait for bro script to send list of vars
#	## [(var_name, var_type), ...]
#	## note: in the future, do this as a call back
#	# store vars in dictionary

def do_setvar(splitLine):
	#setvar a 1.1.1.1 b 2.2.2.2 c 3.3.3.3 d 4.4.4.4 g 5.5.5.5
	#why doesn't it run a on the firts go?
	bc.send("setvar",string("BOGUS"),string("BOGUS"))
	#bogus is a stopgap
	for i in range (1,len(splitLine)-1,2):
		bc.send("setvar",string(splitLine[i]),string(splitLine[i+1])) 
		#sends the list in 2s 
		user_dict[splitLine[i]] = splitLine[i+1]
		#adds each element to a local user_dict
	
#   # splitLine[1] will be var name (e.g., broblemetic_users)
#   # splitLine[2] will be var value (e.g., eric)
#   # if var is an arry, then splitLine will have more vals
#   #   (e.g., eric, alex, oliver)
#   # look up var name in dictionary,
#   # store the value in dictionary
#   # send var name and value to bro device

def do_update(splitLine):
	return
#   # splitLine will not have anything else
#   # send command to bro device to send back
#   #   current values of all vars
#   # store vals in dictionary
#   # call do_list

def do_list(splitLine):
	print user_dict
	return
#   # for each var in dictionary,
#   # print varname and value

def do_help(splitLine):
	return 
#   # print list of commands and options

term()
