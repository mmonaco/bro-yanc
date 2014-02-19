#! /usr/bin/env python

from broccoli import *
import time as Time
import re

global recv 
# we will use recv as a counter for when our event actually runs 
global recv_counter
# recv counter will wait until the event is completed 

recv = 0 
recv_counter = 1

bc = Connection("127.0.0.1:47758")
#intialize connection 

user_dict ={}
#this maps the variables on the bro end to variables on our end 
var_dict = {}
#this maps variables on bro to 

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
	global recv_counter
	global recv
	#initalize the two recievers 
	bc = Connection("127.0.0.1:47758")
	#makes the connection

	bc.send("init_update")
	#initiate init_update, which will send back to the python script from the bro

	while True:
		bc.processInput();

		if recv > recv_counter:
			recv_counter = (recv + 1)
			#recv counter needs to be set one larger at the end of this so it can be ready to wait for the next test properly
			break
		Time.sleep(1)

	do_list()
	#list out the stuff in the dictionary



def do_setbro(splitLine):
#BRO FILE needs to have variables declared on line with no spaces. 
	for line in open(splitLine[1]):
	#opens up our bro file
		if (":" or "=") in line:
		#iterates through each line that contains : or = 
			x = line.split()
			#split it into pieves
			if x[0] == ("global" or "local"):
			#check if the definer is global or local 
				bro_var = x[1].split(":" or "=",1)[0]
				#this is the variable on the bro end stripped down
				bro_var_type = x[1].split(":" or "=",1)[1]
				#this is the other part that the variable equals
				#TODO find a way to split down the second part, what the variable actually equals so that its just the type and not anything else. 
				var_dict[bro_var] = bro_var_type
	print var_dict


	return

def do_setvar(splitLine):
	#setvar brick rick brob rob blane lane
	#why doesn't it run a on the firts go?

	if (len(splitLine) % 2 != 1):
		print "Wrong numbe of varaibles"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(splitLine)-1,2):
			#sends the list in 2s
			bc.send("setvar",string(splitLine[i]),string(splitLine[i+1])) 

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
	user_dict[a] = b

	global recv
	recv += 1 


	

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