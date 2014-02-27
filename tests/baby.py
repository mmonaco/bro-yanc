#! /usr/bin/env python

from broccoli import *
import time as Time

bc = Connection("127.0.0.1:47758")

@event
def reciever(id,val):
	print id
	print val

if bc.connect:
	print "connected."
	while True:
		#ev = Event.new("Control::id_value_request")
		#ev.insert("hello", string)
		#print "sending event"
		bc.send("Control::id_value_request",string("hello"))
		Time.sleep(1)
		print "processing input"
		#bc.process_input