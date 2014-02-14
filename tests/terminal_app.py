#! /usr/bin/env python

from broccoli import *
import time as Time

global recv 
recv = 0 

bc = Connection("127.0.0.1:47758")

user_dict ={}

my_record = record_type("a","b")

def term():
	print ("\nTerminal to Bro Device. Type 'help' for commands")
	while True:	
		n = raw_input("\n>> ")

		commands = ["update","setbro","help","list","setvar","quit"]

		splitLine = (n.lower()).split()
		
		if splitLine[0] == commands[0]: 
			#update
			update_waiter()

		if splitLine[0] == commands[1]:
			#setbro
			do_setbro(splitLine)
		
		if splitLine[0] == commands[2]:
			#help
			do_help(splitLine)

		if splitLine[0] == commands[3]: 
			#list
			do_list()

		if splitLine[0] == commands[4]: 
			#setvar
			do_setvar(splitLine)

		if splitLine[0] == commands[5]:
			#quit
			break

		if not splitLine[0] in commands:
			print ("Do you need help? Type 'help' for a list of possible commands.")


def update_waiter():
	bc = Connection("127.0.0.1:47758")
	#makes the connection

	bc.send("init_update")
	#initiate init_update, which will send back to the python script from the bro

	while True:
		bc.processInput();
		if recv > 1:
			break
		Time.sleep(1)
	do_list()



def do_setbro(splitLine):
	return
	#What exactly does this mean? 
#	# splitLine[1] is a bro script file name
#	# send bro script to bro device
#	# wait for bro script to send list of vars
#	## [(var_name, var_type), ...]
#	## note: in the future, do this as a call back
#	# store vars in dictionary

def do_setvar(splitLine):
	#setvar brick rick brob rob blane lane
	#why doesn't it run a on the firts go?
	for i in range (1,len(splitLine)-1,2):
		bc.send("setvar",string(splitLine[i]),string(splitLine[i+1])) 
		#sends the list in 2s

		#user_dict[splitLine[i]] = splitLine[i+1]

		#adds each element to a local user_dict ->should i do this or just wait for update?

	
#   # splitLine[1] will be var name (e.g., broblemetic_users)
#   # splitLine[2] will be var value (e.g., eric)
#   # if var is an arry, then splitLine will have more vals
#   #   (e.g., eric, alex, oliver)
#   # look up var name in dictionary,
#   # store the value in dictionary
#   # send var name and value to bro device
#DONE 


@event
def update(a,b):
   global recv
   recv += 1 
   user_dict[a] = b 
   # adds a dictionary for user a to be user b

#   # splitLine will not have anything else
#   # send comand to bro device to send back
#   #   current values of all vars
#   # store vals in dictionary
#   # call do_list
#DONE

def do_list():
	print user_dict
	return
#   # for each var in dictionary,
#   # print varname and value

def do_help(splitLine):
	print("\nSupported commands are:\n")
	print("list -- which lists out all of the locally stored variable names and values\n")
	print("Example: >> list\n")
	print("update -- which updates the values of your local variables to those on the bro device\n")
	print("Example: >> update\n")
	print("setvar -- which takes in an array of strings, seperated by spaces, and creates a record on the bro device that maps the first string to the second\n")
	print("Example: >> setvar brick rick brob rob\n")
	print("quit -- which quits the program\n")
	print("Example: >> quit")
	return 

if __name__ == "__main__":
	term()