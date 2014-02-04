#! /usr/bin/env python

import csv
from broccoli import *
#the parser
materials = []
def importer():
	with open('sample.csv','rU') as f: 
		mycsv = csv.reader(f)
		for row in mycsv:
			text = row[0]
			materials.append(text)

importer()

#TODO: Get the importer to craft individual params for test1 AND figure out a way to past array 
# for i in range (len(materials)-1):
# 	print materials[i]
# 	bc.send("test1",materials[i])


bc = Connection("127.0.0.1:47758")

@event(addr)

def test1(i):
	print i #don't know why this happens 

bc.send("test1",addr("6.7.7.4")) #sends the tests 
bc.send("test1",addr("1.1.1.1"))
bc.send("test1",addr("1.1.1.5"))
bc.send("test2") #this is the printer to print out the users 
####################################################################

 


