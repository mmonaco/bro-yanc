#! /usr/bin/env python

import csv
from broccoli import *
#the parser
materials = [] #array of ips to send
def importer(): #the parser
	with open('sample.csv','rU') as f: 
		mycsv = csv.reader(f)
		for row in mycsv:
			text = row[0]
			materials.append(text)

importer()

bc = Connection("127.0.0.1:47758") #opens the connection to the bro box 

@event(addr) #creates the new event to send the addr

def test1(i):
	print i 

for i in range(len(materials)): 
	bc.send("test1",addr(materials[i]))
	
bc.send("test2") #this is the printer to print out the users 
####################################################################

#To demonstate: :~/Documents/broc_yanc/broccoli_python/tests$ python broblem_sender.py
#user@user-VirtualBox:/usr/local/bro/scripts$ ./../bin/bro ~/Documents/broc_yanc/broccoli_python/tests/alex_test.bro 

 


