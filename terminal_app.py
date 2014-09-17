#! /usr/bin/env python

# Proper way to use the program: 
# 1. Create a sample bro script. 
# 2. While writing the bro script, instead of using normal variables make it yanc::user_set[x] (finishing this up)
# 3. Create a custom module using do_create_module
# 4. "yancify" the script using the do_modify_script
# 5. Send the script to proper directory on the device
# 6. Send the module to the frameworks directory 
# 7. Run the bro script and start changing stuff from the terminal_app

# Notes: All of the connections between the controller and the bro device are kept in custom module, so when the script is being written
# the only thing the writer needs to worry about is making the variables look at the module, which can use the placeholder value of yanc:: because 
# our script modifer will change the actual module name and any references. 

from tempfile import mkstemp
from broccoli import *

import shutil
import os 
import time as Time
import re
import paramiko
import fileinput

#recieved is incremented by one every time an event is sent from bro to the script and properly recieved 
global recieved 
recieved = 0 

#list of open_connections to different bro devices 
global open_connections
open_connections = []

#temp_dict is populated by the update method and then flushed into bro_connection.var_dict
temp_dict ={}

myRecord = record_type("host_name","ip_address")

class bro_connection: 

	name = ""
	var_dict = {}
	ip_port = ""
	recvieved_counter=1
	connection = ""

	def __init__(self,ip_port,name):

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
		commands = ["ls_var","help","list","set_addr","delvar","quit","connect","test",
					"update_all","current_connection","connections","set_connection",
					"send_script","module","modify_script","demo","set_string","set_int"]

		#Comments on top of splitline is syntax
		#try:
		# quit
		if split_line[0] == "quit":
			break

		# help
		if split_line[0] == "help":
			do_help(split_line)

		#set_connection (connection_name)	
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

		#current_connection 		
		if split_line[0] == "current_connection":
			if (current_connection):
				print ("Connected to: " + current_connection.ip_port + " with " + current_connection.name)
			else:
				print("No current connection to any device, maybe use the 'connect' command?")
		#connections
		if split_line[0] == "connections":
			for i in open_connections:
				print i.name

		#connect 127.0.0.1:47758 bro1
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

		#These commands require there to be an active connection to work 

		if (current_connection): 	
			# ls_var
			if split_line[0] == "ls_var": 
				temp_dict.clear()
				do_update_waiter(current_connection)

			# list
			if split_line[0] == "list": 
				do_list(current_connection)

			# set_addr foo 255.255.255.255
			if split_line[0] == "set_addr": 
				do_set_addr(split_line,current_connection)

			# set_int foo 4
			if split_line[0] == "set_int": 
				do_set_int(split_line,current_connection)

			# set_string foo bar 
			if split_line[0] == "set_string": 
				do_set_string(split_line,current_connection)

			# delvar foo 255.255.255.255
			if split_line[0] == "delvar": 
				do_delvar(split_line,current_connection)

			# update_all
			if split_line[0] == "update_all":
				do_update_all()

			if split_line[0] == "demo":
				do_demo(current_connection)
		########################################
		#These are for prepping/sending scripts#
		########################################

		# module (name) (port)
		if split_line[0] == "module":
			do_create_module(split_line[1],split_line[2])

		# modify_script (bro file) (module_name)
		if split_line[0] == "modify_script":
			do_modify_script(split_line[1],split_line[2])

		# send_script (Dest ip) (Dest username) (Dest password) (brofile localpath) (dest filename)
		if split_line[0] == "send_script":
			print("howdy")
			do_send_script("127.0.0.1","user","user","/home/user/Documents/broc_yanc/broccoli_python/testfile","twit")

		# #this is if they are trying to press enter with nothing actually in the line
		# except IndexError:

		# 	#this is when i make the quick connection via "connect bro1" or "connect bro2"
		# 	if (split_line[1] == "bro1" or "bro2"):
		# 		print("shortcut connection made")

		# 	else:
		# 		print("Make sure your command has the proper arguments!")

		# #this is for when user is entering an invalid ip:port string
		# except ValueError:
		# 	print("Your ip/port is invalid, use the proper syntax: 127.0.0.1:47758")

		# #this handles an error thrown when we try to make a connection from a the python script to an invalid bro device
		# except socket.error:
		# 	print ("Your I{} address in invalid")

		# # #When trying to connect to a bro device fails
		# except IOError:
		# 	#if user has ever even initated a connection
		# 	if(current_connection):
		# 		print ("Can't reach the bro device at: " + current_connection.name + " with " + current_connection.ip_port)
		
		# 	else:
		# 		print ("Can't contact bro device")

###########################################################################################
#END OF TERMINAL APP#######################################################################
###########################################################################################

#This is the method that recieves the update information from bro and populates the dictionary 
@event
def update(variable,ip_address):
	print("recieved " + variable + " and " + ip_address)

	if not (variable == "default" and ip_address == "0.0.0.0"):
		temp_dict[variable] = ip_address

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
def do_set_addr(split_line,bro_connection):

	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in twos
			bro_connection.connection.send("set_addr",string(split_line[i]),addr(split_line[i+1])) 

	print("Set address successfuly on " + bro_connection.name)

def do_set_string(split_line,bro_connection):

	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in twos
			bro_connection.connection.send("set_string",string(split_line[i]),string(split_line[i+1])) 

	print("Set string successfuly on " + bro_connection.name)

def do_set_int(split_line,bro_connection):

	if (len(split_line) % 2 != 1):
		print "Wrong numbe of variables"
	#checks if there are an odd number of variables input 
	else: 
		for i in range (1,len(split_line)-1,2):
			#sends the list in twos
			bro_connection.connection.send("set_int",string(split_line[i]),int(split_line[i+1])) 

	print("Set int successfuly on " + bro_connection.name)


def do_demo(bro_connection):
	bro_connection.connection.send("bro_demo") 

#This deletes a variable in the bro set. 
def do_delvar(split_line,bro_connection):

	for i in range (1,len(split_line)-1):
		bro_connection.connection.send("delvar",string(split_line[i])) 

#This lists out the varaibles in the dictionary 
def do_list(bro_connection):
	print (bro_connection.var_dict)

#This goes through all open connections and calls update on all of them.
#UNDER CONSTRUCTION!!!
def do_update_all():
	for connection in open_connections:
		do_update_waiter(connection)
		print("++++++++++++++++++")

#This takes the template module from /yanc/main.bro and edits features to create a custom module for a bro script 
def do_create_module(name,port):

	#this creates the new module directory 
	mypath = name
	if not os.path.isdir(mypath):
	   os.makedirs(mypath)

	#this copies the template files from the template directory to our new directory
	shutil.copyfile('./yanc/main.bro', "./" + mypath + "/template_main.bro")
	shutil.copyfile('./yanc/__load__.bro', "./" + mypath + "/__load__.bro")
	
	#this opens up the template and starts chaning stuff around 
	template_main = open("./" + mypath + "/template_main.bro", 'r')
	real_main = open("./" + mypath + "/main.bro", 'wr')
	
	#this is where to add different replacements. More will be added over time, match these with the parameters for the function so the user can control this
	for line in template_main:

		if line.strip() == ("redef Communication::listen_port = 47758/tcp;"):
			real_main.write("redef Communication::listen_port = " + port + ";")
			
		elif line.strip() == ("module yanc;"):
			real_main.write("module " + name + ";\n")

		else:
			real_main.write(line)

	#this closes the files and removes the leftover template
	template_main.close
	real_main.close()
	os.remove("./" + mypath + "/template_main.bro")
#This function is given a bro file as a param and does the following:
# 1. Creates a copy in the same directory
# 2. Goes through copy and removes all references to predefined module
# 3. Replaces them with references to module that we made.

def do_modify_script(bro_file,module_name):

	mod_file_string =  bro_file.replace(".bro","_yanced.bro")
	shutil.copyfile(bro_file,mod_file_string)

	template_main = open(bro_file, 'r')
	real_main = open(mod_file_string, 'wr')
	#this is where to add different replacements. More will be added over time, match these with the parameters for the function so the user can control this
	for line in template_main:
		real_main.write(line.replace('yanc', module_name))

	#this closes the files and removes the leftover template
	template_main.close()
	real_main.close()

#This takes the newly modified script, sends it to the proper host via ssh for it to be run. 
def do_send_script(host,username,password,path,filename):

	host = "127.0.0.1"
	port = 22
	transport = paramiko.Transport((host, port))
	transport.connect(username = username, password = password)
	sftp = paramiko.SFTPClient.from_transport(transport)

	filepath = '/home/user/bro/scripts/yanc/' + filename
	localpath = path
	sftp.put(localpath, filepath)

	sftp.close()
	transport.close()

def do_help(split_line):
	print("\nSupported commands are:\n")
	print("list -- which lists out all of the locally stored variable names and values\n")
	print("Example: >> list\n")
	print("update -- which updates the values of your local variables to those on the bro device\n")
	print("Example: >> update\n")
	print("set_addr -- which takes in an array of strings, seperated by spaces, and creates a record on the bro device that maps the first string to the second\n")
	print("Example: >> set_addr a 1.1.1.1 b 2.2.2.2\n")
	print("quit -- which quits the program\n")
	print("Example: >> quit")
	return 

if __name__ == "__main__":
	term()