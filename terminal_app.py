#! /usr/bin/env python

from broccoli import *
import time as Time
import re

#recieved is incremented by one every time an event is sent from bro to the script and properly recieved 
global recieved 
recieved = 0 

global open_connections
open_connections = []

global temp_dict
temp_dict ={}

myRecord = record_type("host_name","ip_address")

class bro_connection: 

	name = ""
	var_dict = {}
	ip_port = ""
	recvieved_counter=1
	connection = ""

	port_regex = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{0,5})")

	def __init__(self,ip_port,name):

		if not (self.port_regex.match(ip_port)):
			raise ValueError()

		self.ip_port = ip_port
		self.name = name

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

###########################################################################################
# This launches the actual terminal process where we will call the differnet methods from # 
###########################################################################################
def term():

	current_connection = ""

	print ("\nTerminal to Bro Device. Type 'help' for commands")

	while True:	
		n = raw_input("\n>> ")

		split_line = (n.lower()).split()

		#add new commands here so we can tell valid/invalid commands 
		commands = ["ls_var","help","list","setvar","delvar","quit","connect","test",
					"update_all","current_connection","connections","set_connection"]

		try:
			#Syntax: quit
			if split_line[0] == "quit":
				break

			if split_line[0] == "set_connection":
				try:
					for connection in open_connections:
						print ("connection.name is: " + connection.name + "arg is " + split_line[1])
						if connection.name == split_line[1]:
							current_connection=connection
							break
						else:
							print("connection name not found")
				except:
					print("Include a name with the following format: set_connection local")
			
			#Syntax: help
			if split_line[0] == "help":
				do_help(split_line)

			#for dev testing, can fill this out with other random stuff
			if split_line[0] == "current_connection":
				if (current_connection):
					print ("Connected to: " + current_connection.ip_port + " with " + current_connection.name)
				else:
					print("No current connection to any device, maybe use the 'connect' command?")

			if split_line[0] == "connections":
				for i in open_connections:
					print i.name

			#Syntax: connection 127.0.0.1:47758
			if split_line[0] == "connect":
				make = True

				if split_line[1] == "bro1":
					open_connections.append(bro_connection("127.0.0.1:47758","bro1"))
					open_connections[-1].open_connection()
					current_connection = open_connections[-1]

				if split_line[1] == "bro2":
					open_connections.append(bro_connection("127.0.0.1:47759","bro2"))
					open_connections[-1].open_connection()
					current_connection = open_connections[-1]

				#This is used for making sure no duplicate connection is made 
				for connection in open_connections:
					if (connection.name == split_line[2] or connection.ip_port == split_line[1]):
						make = False
						
						if not make:
							print("Connection already made at: " + connection.ip_port + " with name " + connection.name)

				if (make):
					open_connections.append(bro_connection(split_line[1],split_line[2]))
					open_connections[-1].open_connection()
					current_connection=open_connections[-1]

			
			if not split_line[0] in commands:
				print ("Do you need help? Type 'help' for a list of possible commands.")

			#These commands require there to be an active connection 	
			if (current_connection): 	
				#Syntax: update
				if split_line[0] == "ls_var": 
					temp_dict.clear()
					do_update_waiter(current_connection)

				#Syntax: list
				if split_line[0] == "list": 
					do_list(current_connection)

				#Syntax: setvar foo 255.255.255.255
				if split_line[0] == "setvar": 
					do_setvar(split_line,current_connection)

				#Syntax: delvar foo 255.255.255.255
				if split_line[0] == "delvar": 
					do_delvar(split_line,current_connection)

				#this goes through all of the dictionaries
				if split_line[0] == "update_all":
					do_update_all()

		#this is if they are trying to press enter with nothing actually in the line
		except IndexError:

			#this is when i make the quick connection via "connect bro1" or "connect bro2"
			if (split_line[1] == "bro1" or "bro2"):
				print("shortcut connection made")

			else:
				print("Make sure your command has the proper arguments!")

		#this is for when user is entering an invalid ip:port string
		except ValueError:
			print("Your ip/port is invalid, use the proper syntax: 127.0.0.1:47758")

		#this handles an error thrown when we try to make a connection from a the python script to an invalid bro device
		except socket.error:
			print ("Your Ip address in invalid")

		#When trying to connect to a bro device fails
		except IOError:
			#if user has ever even initated a connection
			if(current_connection):
				print ("Can't reach the bro device at: " + current_connection.name + " with " + current_connection.ip_port)
		
			else:
				print ("Can't contact bro device")
#This is the method that recieves the update information from bro and populates the dictionary 
@event
def update(device_name,ip_address):
	print("recieved " + device_name + " and " + ip_address)

	if not (device_name == "default" and ip_address == "0.0.0.0"):
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

	print("Set varaible successfuly on " + bro_connection.name)

#This deletes a variable in the bro set. 
def do_delvar(split_line,bro_connection):

	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in twos
			bro_connection.connection.send("delvar",string(split_line[i]),addr(split_line[i+1])) 

#This lists out the varaibles in the dictionary 
def do_list(bro_connection):
	print (bro_connection.var_dict)

#This goes through all open connections and calls update on all of them.
def do_update_all():
	for connection in open_connections:
		do_update_waiter(connection)
		print("++++++++++++++++++")

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