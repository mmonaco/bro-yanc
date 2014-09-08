#! /usr/bin/env python

from broccoli import *
import time as Time
import re

#recieved is incremented by one every time an event is sent from bro to the script and properly recieved 
global recieved 
recieved = 0 

temp_dict ={}
#this maps the variables on the bro end to variables on our end  
global open_connections
open_connections = []

myRecord = record_type("a","b")

class bro_connection: 

	var_dict = {}
	ip_port = ""
	recvieved_counter=1
	connection = ""

	port_regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})")

	def __init__(self,ip_port):

		if not (self.port_regex.match(ip_port)):
			raise ValueError()

		self.ip_port = ip_port

	def open_connection(self):
		self.connection = Connection(self.ip_port)

	def increment_recv_counter(self,recieved):
		self.recvieved_counter = recieved + 1 

	def wait(self):
		while True:

			self.connection.processInput()

			global recieved

			if recieved >= self.recvieved_counter:
				self.increment_recv_counter(recieved)
				break

			Time.sleep(1)

#####
#This launches the actual terminal process where we will call the differnet methods from 
#####
def term():

	test_connection = ""

	print ("\nTerminal to Bro Device. Type 'help' for commands")

	while True:	
		n = raw_input("\n>> ")

		split_line = (n.lower()).split()

		#add new commands here so we can tell valid/invalid commands 
		commands = ["update","setscript","help","list","setvar","delvar","quit","connection","test","q"]

		try:
			#Syntax: update
			if split_line[0] == "update": 
				temp_dict.clear()
				do_update_waiter(test_connection)
			
			#Syntax: setscript (UNDER CONSTRUCTION)
			if split_line[0] == "setscript":
				do_set_script(split_line)
			
			#Syntax: help
			if split_line[0] == "help":
				do_help(split_line)

			#Syntax: list
			if split_line[0] == "list": 
				do_list(test_connection)

			#Syntax: setvar foo 255.255.255.255
			if split_line[0] == "setvar": 
				do_setvar(split_line,test_connection)

			#Syntax: delvar foo 255.255.255.255
			if split_line[0] == "delvar": 
				do_delvar(split_line,test_connection)

			#Syntax: quit
			if split_line[0] == ("quit" or "q"):
				break

			#Syntax: connection 127.0.0.1:47758
			if split_line[0] == "connection":

				if split_line[1] == "local":
					open_connections.append(bro_connection("127.0.0.1:47758"))
					open_connections[-1].open_connection()
					test_connection = open_connections[-1]

				else:
					open_connections.append(bro_connection(split_line[1]))
					open_connections[-1].open_connection()
					test_connection = open_connections[-1]

			if split_line[0] == "test":
				print open_connections

			#if they typed in an invalid command
			if not split_line[0] in commands:
				print ("Do you need help? Type 'help' for a list of possible commands.")

		#this is if they are trying to press enter with nothing actually in the line
		except IndexError:
			print("Make sure you have have some content!")

		except ValueError:
			print("Your ip/port is invalid, use the proper syntax: 127.0.0.1:47758")

#This is the method that recieves the update information from bro and populates the dictionary 
@event
def update(device_name,ip_address):
	print("recieved ", device_name, " and", ip_address)
	temp_dict[device_name] = ip_address

	#when we recieved the info from bro, we incrmenet the recieved counter by 1. 
	global recieved
	recieved += 1 

#This waits for the update info to be sent from the bro device. 
def do_update_waiter(bro_connection):

	global temp_dict

	#we init the update and start waiting for the response
	bro_connection.connection.send("init_update")
	bro_connection.wait()

	#response are saved globally in temp_dict (this is becaue I couldn't get bro to send me the individual connection objects for each connection)
	bro_connection.var_dict = temp_dict
	#the temp dict is then put into the connection object, and the temp dict is cleared for the next connection to add to it. 
	temp_dict.clear

	do_list(bro_connection)
	#list out the stuff in the dictionary

#This sends the variable to the bro device to be added to the user set. 
def do_setvar(split_line,bro_connection):

	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in twos
			bro_connection.connection.send("setvar",string(split_line[i]),addr(split_line[i+1])) 

#This deletes a variable in the bro set. 
def do_delvar(split_line,bro_connection):

	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in twos
			bro_connection.connection.send("delvar",string(split_line[i]),addr(split_line[i+1])) 

#TODO in future
#This should be used to parse the scripts to send to a bro device. 
def do_set_script(split_line):
	bro_file = open(split_line[1], 'w')
	

#This lists out the varaibles in the dictionary 
def do_list(bro_connection):
	print (bro_connection.var_dict)

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