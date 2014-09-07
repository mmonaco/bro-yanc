#! /usr/bin/env python

from broccoli import *
import time as Time
import re

global bc 
#bc = Connection("127.0.0.1:47758")

global recv 
recv = 0 
# we will use recv as a counter for when our event actually runs 

global recv_counter
recv_counter = 1
# recv counter will wait until the event is completed 

user_dict ={}
#this maps the variables on the bro end to variables on our end  

myRecord = record_type("a","b")

class bro_connection: 
	var_dict = {}
	ip_port = ""
	recv = 0
	recv_counter=1
	connection = ""

	port_regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})")

	def __init__(self,ip_port):
		self.ip_port = ip_port

		if(self.port_regex.match(ip_port)):
			print("Good connection!")
			#bro_connection = Connection(ipBro)
		else:
			print("Bad connection!")

	def open_connection(self):
		self.connection = Connection(self.ip_port)

	def increment_recv(self):
		self.recv = self.recv + 1

	def increment_recv_counter(self):
		self.recv_counter = self.recv_counter + 1 

	def wait(self):
		if recv >= recv_counter:
			recv_counter = (recv + 1)

#####
#This launches the actual terminal process where we will call the differnet methods from 
#####
def term():

	device = "127.0.0.1:47758"
	#device = raw_input("Input a port & ip: ")
	test_connection = bro_connection(device)
	test_connection.open_connection()

	print ("\nTerminal to Bro Device. Type 'help' for commands")

	while True:	
		n = raw_input("\n>> ")

		split_line = (n.lower()).split()

		commands = ["update","setscript","help","list","setvar","delvar","quit","connection"]

		try:
			#Syntax: update
			if split_line[0] == commands[0]: 
				user_dict.clear()
				do_update_waiter()
			
			#Syntax: setscript (UNDER CONSTRUCTION)
			if split_line[0] == commands[1]:
				do_set_script(split_line)
			
			#Syntax: help
			if split_line[0] == commands[2]:
				do_help(split_line)

			#Syntax: list
			if split_line[0] == commands[3]: 
				do_list()

			#Syntax: setvar foo 255.255.255.255
			if split_line[0] == commands[4]: 
				do_setvar(split_line,test_connection)

			#Syntax: delvar foo 255.255.255.255
			if split_line[0] == commands[5]: 
				do_delvar(split_line)

			#Syntax: quit
			if split_line[0] == commands[6]:
				break

			#Syntax: connection 127.0.0.1:47758
			if split_line[0] == commands[7]:
				test_connection = bro_connection(split_line[1])
				test_connection.open_connection()

			if not split_line[0] in commands:
				print ("Do you need help? Type 'help' for a list of possible commands.")

		except IndexError:
			print("Make sure you have have some content!")

#This is the method that recieves the update information from bro and populates the dictionary 
@event
def update(device_name,ip_address):
	print("recieved ", device_name, " and", ip_address)
	user_dict[device_name] = ip_address

	global recv
	recv += 1 

#TODO -- possibly pass different connection objects as parameters so I can work on each individual connection 
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
def do_setvar(split_line,bro_connection):
	#try:
	bro_connection.connection.send("") 
	bro_connection.connection.send("bro_list")
	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in 2s
			bro_connection.connection.send("setvar",string(split_line[i]),addr(split_line[i+1])) 

	# except:
	# 	print("Error")

#This deletes a variable in the bro set. 
def do_delvar(split_line):
	try: 
		print ("Delvar runs!")
		if (len(split_line) % 2 != 1):
			print "Wrong numbe of variables"
		#checks if there are an odd number of variables input 
		else: 
			for i in range (1,len(split_line)-1,2):
				#sends the list in 2s
				bc.send("delvar",string(split_line[i]),addr(split_line[i+1])) 
		
		bc.send("bro_list")

	except:
		print("Error")

#TODO in future
#This should be used to parse the scripts to send to a bro device. 
def do_set_script(split_line):
	bro_file = open(split_line[1], 'w')
	

#This lists out the varaibles in the dictionary 
def do_list():
	print user_dict

def do_help(split_line):
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