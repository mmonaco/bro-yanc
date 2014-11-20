#!/usr/bin/env python2

from __future__ import print_function

import os, os.path
import cmd
import readline
import shlex
from   bro.connection import BroConnection
from   bro.script     import BroScript
from   bro.util       import *

USAGE = """\
Welcome to the Yanc Bro Shell!

 This shell is for interaction with remote Bro IDSs. Type 'help' for a list
 of commands and 'help <command>' for a brief overview of a specific command.
 Basic readline support is enabled and history is preserved.

 The shell keeps track of multiple connections, with one connection being
 active at a time. Each connection is implemented using an SSH/SFTP tunnel.

   connect: connect to a Bro IDS and mark it as the current connection
   use:     mark one of the connected Bros as the current connection
   ls:      view a list of current connections and their aliases

 Each connection can have multiple scripts loaded, and each script can be either
 running or stopped

   load:    load a .bro script and transfer it to the current remote Bro IDS
   run:     run a .bro script which has been loaded
   stop:    stop a .bro script which is running

 While a script is running, its state can be inspected and manipulated

   set_string:  set a string
   set_int:     set an integer
   set_addr:    set an IP address
   ls:          print all variables

 The shell does its best to cleanup after itself. At exit, any files transferred
 to the remote Bro IDS are deleted.

@author: Alex Tsankov
@author: Matt Monaco
"""

class BroShell(cmd.Cmd):

	prompt = "(disconnected)> "

	def __init__(self):

		cmd.Cmd.__init__(self)
		self.connections = dict()
		self.cur_cxn     = None
	
		self.histfile = os.path.expanduser("~/.cache/bro_history")
		try:
			readline.read_history_file(self.histfile)
		except IOError:
			pass

	def cleanup(self):

		for cxn in self.connections.values():
			cxn.cleanup()
		readline.write_history_file(self.histfile)

	def __parse_args(self, line, num):

		args  = shlex.split(line)
		num_unset = num - len(args)
		return args + [None]*num_unset

	def do_connect(self, line):
		"""connect [user@]host[:port] [alias]"""
		try:
			host, alias = self.__parse_args(line, 2)

		except ValueError as ve:
			print("error: too many arguments")
			return

		if not host:
			print("error: a hostname is required")
			return
		if not alias:
			alias = host

		host, user, port = parse_ssh_hostname(host)

		if alias in self.connections:
			print("error: %s already connected as %s" % (self.connections[alias].address, alias))
			return

		try:
			self.connections[alias] = BroConnection(alias, host, port, user)
		except Exception as e:
			print("error connecting: " + str(e))
			return

		self.do_use(alias)

	def do_ls(self, line):
		"""ls [alias]"""
		alias, = self.__parse_args(line, 1)
		if alias:
			print("ALIAS", alias)
			return
		else:
			for alias, cxn in self.connections.items():
				print(alias, str(cxn))  

				for scriptname, script in cxn.scripts.items():
					print("\t", scriptname)

					for key, val in script.int_cache.items():
						print("\t\tint   ",key,"=",val)
					for key, val in script.string_cache.items():
						print("\t\tstring",key,"=",val)
					for key, val in script.int_cache.items():
						print("\t\taddr  ",key,"=",val)

	def do_set_int(self, line):
		"""set_int script key value"""
		scriptname, key, value = self.__parse_args(line, 3)
		if self.cur_cxn is None:
			print("error: no connection")
			return
		elif scriptname not in self.cur_cxn.scripts:
			print("error: unknown script '%s'" % (scriptname))
			return
		script = self.cur_cxn.scripts[scriptname]
		script.set_int(key, value)

	def do_set_string(self, line):
		"""set_string script key value"""
		scriptname, key, value = self.__parse_args(line, 3)
		if self.cur_cxn is None:
			print("error: no connection")
			return
		elif scriptname not in self.cur_cxn.scripts:
			print("error: unknown script '%s'" % (scriptname))
			return
		script = self.cur_cxn.scripts[scriptname]
		script.set_string(key, value)

	def do_set_addr(self, line):
		"""set_addr script key value"""
		scriptname, key, value = self.__parse_args(line, 3)
		if self.cur_cxn is None:
			print("error: no connection")
			return
		elif scriptname not in self.cur_cxn.scripts:
			print("error: unknown script '%s'" % (scriptname))
			return
		script = self.cur_cxn.scripts[scriptname]
		script.set_addr(key, value)

	def do_use(self, alias):
		"""use alias"""
		if alias not in self.connections:
			print("error: unknown alias '%s'" % (alias,))
			return
		self.cur_cxn = self.connections[alias]
		BroShell.prompt = alias + "> "

	def do_load(self, line):
		"""load path [name]"""
		if self.cur_cxn is None:
			print("error: no connection")
			return
		path, name = self.__parse_args(line, 2)
		if name is None:
			name = os.path.basename(path)
		self.cur_cxn.load(path, name)

	def do_run(self, scriptname):
		"""run name"""
		if self.cur_cxn is None:
			print("error: no connection")
			return
		self.cur_cxn.run(scriptname)

	def do_stop(self, scriptname):
		"""stop name"""
		if self.cur_cxn is None:
			print("error: no connection")
			return
		self.cur_cxn.stop(scriptname)

	def do_EOF(self, line):
		"""CRTL-D to exit"""
		print()

	def postcmd(self, stop, line):
		if line == "EOF":
			return True

# vim: set noet ts=8 sts=8 sw=0 :
