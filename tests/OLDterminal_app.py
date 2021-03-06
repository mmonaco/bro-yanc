#! /usr/bin/env python

from broccoli import *
import time as Time
import re

global bc 
global recv 
# we will use recv as a counter for when our event actually runs 
global recv_counter
# recv counter will wait until the event is completed 
recv = 0 
recv_counter = 1
bc = Connection("127.0.0.1:47758")

user_dict ={}
#this maps the variables on the bro end to variables on our end  

my_record = record_type("a","b")

#####
#This launches the actual terminal process where we will call the differnet methods from 
#####
def term():

	print ("\nTerminal to Bro Device. Type 'help' for commands")

	#This regex is used to test for a valid ip address to connect to a bro device 
	regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})")
	ipBro = raw_input("Ip and port of a bro device you want to connect to(def- 127.0.0.1:47758): ")
	
	#if the address is valid, then set that as the address
	if(regex.match(ipBro)):
		global bc 
		bc = Connection(ipBro)

	while True:	
		n = raw_input("\n>> ")

		splitLine = (n.lower()).split()

		commands = ["update","setscript","help","list","setvar","delvar","quit"]

		try:
			if splitLine[0] == commands[0]: 
				#update
				user_dict.clear()
				do_update_waiter()
			
			if splitLine[0] == commands[1]:
				#setbro
				do_set_script(splitLine)
			
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
				#setvar
				do_delvar(splitLine)

			if splitLine[0] == commands[6]:
				#quit
				break

			if not splitLine[0] in commands:
				print ("Do you need help? Type 'help' for a list of possible commands.")

		except IndexError:
			print("Make sure you have have some content!")

#This is the method that recieves the update information from bro and populates the dictionary 
@event
def update(deviceName,ipAddress):
	print("recieved ", deviceName, " and", ipAddress)
	user_dict[deviceName] = ipAddress

	global recv
	recv += 1 

#This waits for the update info to be sent from the bro device. 
def do_update_waiter():
	global recv_counter
	global recv
	#initalize the two recievers 
	bc = Connection("127.0.0.1:47758")
	#makes the connection
	bc.send("init_update")
	#initiate init_update, which will send back to the python script from the bro

	while True:
		bc.processInput();
		if recv >= recv_counter:
			recv_counter = (recv + 1)
			#recv counter needs to be set one larger at the end of this so it can be ready to wait for the next test properly
			break
		Time.sleep(1)

	do_list()
	#list out the stuff in the dictionary

#This sends the variable to the bro device to be added to the user set. 
def do_setvar(splitLine):
	try: 
		bc.send("bro_list")
		if (len(splitLine) % 2 != 1):
			print "Wrong numbe of variables"
		#checks if there are an odd number of variables input 
		else: 
			for i in range (1,len(splitLine)-1,2):
				#sends the list in 2s
				bc.send("setvar",string(splitLine[i]),addr(splitLine[i+1])) 
	
	except:
		print("Error")

def do_delvar(splitLine):
	try: 
		print ("Delvar runs!")
		if (len(splitLine) % 2 != 1):
			print "Wrong numbe of variables"
		#checks if there are an odd number of variables input 
		else: 
			for i in range (1,len(splitLine)-1,2):
				#sends the list in 2s
				bc.send("delvar",string(splitLine[i]),addr(splitLine[i+1])) 
		
		bc.send("bro_list")

	except:
		print("Error")


def do_set_script(splitLine):
	broFile = open(splitLine[1], 'w')
	

def do_list():
	print user_dict

def do_help(splitLine):
	print("\nSupported commands are:\n")
	print("list -- which lists out all of the locally stored variable names and values\n")
	print("Example: >> list\n")
	print("update -- which updates the values of your local variables to those on the bro device\n")
	print("Example: >> update\n")
	print("setvar -- which takes in an array of strings, seperated by spaces, and creates a record on the bro device that maps the first string to the second\n")
	print("Example: >> setvar a 1.1.1.1 b 2.2.2.2\n")
	print("quit -- which quits the program\n")
	print("Example: >> quit")
	return 

if __name__ == "__main__":
	term()