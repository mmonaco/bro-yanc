#! /usr/bin/env python

from broccoli import *

bc = Connection("127.0.0.1:47758")

user_dict ={}

my_record = record_type("a", "b")

def term():
	while True:		# infinite loop
		n = raw_input("\n>> ")
		splitLine = n.split()

		if splitLine[0] == "bro_list":
			print "bro_list was typed"  
			do_bro_list()

		if splitLine[0] == "update":
			print "update was typed"  
			init_update()

		if splitLine[0] == "setbro":
			print "setbro was typed and recived" 
			do_setbro(splitLine)
		
		if splitLine[0] == "help":
			print "help was typed and recived" 
			do_help(splitLine)

		if splitLine[0] == "list": 
			do_list(splitLine)

		if splitLine[0] == "setvar": 
			print "setvar was typed and recived"
			do_setvar(splitLine)

		if splitLine[0] == "quit":
			break



def do_setbro(splitLine):
	return
#	# splitLine[1] is a bro script file name
#	# send bro script to bro device
#	# wait for bro script to send list of vars
#	## [(var_name, var_type), ...]
#	## note: in the future, do this as a call back
#	# store vars in dictionary

def do_setvar(splitLine):
	#setvar brick rick brob rob blane lane
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

def init_update():
	print "Init update sent"
	bc.send("init_update")
	bc.processInput()


@event(string,string)
def update(a,b):
	print "do update reicved"
	print a, b



def do_bro_list(): 
	bc.send("bro_list")	

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
#DONE

def do_help(splitLine):
	print("Supported commands are:\n")
	print("bro_list -- which lists out all of the locally stored variable names and values\n")
	print("update -- which ")

	return 
#   # print list of commands and options


if __name__ == "__main__":
    term()