#!/usr/bin/env python2

from __future__ import print_function

import sys
sys.path.append("/usr/local/bro/lib/broctl/")

import os, os.path
import cmd
import readline
import shlex
import broccoli
import paramiko
import re
import time
import threading

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

		host, alias = self.__parse_args(line, 2)

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
			self.connections[alias] = BroConnection(host, port, user)
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

class BroConnection(object):

	def __init__(self, hostname, port=None, user=None):

		self.hostname  = hostname
		self.user      = user
		self.port      = port
		self.address   = format_ssh_hostname(hostname, user, port)

		self.scripts   = dict()

		kwargs = dict()
		if port is not None:
			kwargs["port"] = port
		if user is not None:
			kwargs["username"] = user

		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(hostname, **kwargs)
		self.sftp = self.ssh.open_sftp()

		self.cur_bro_port = 47000

		self.install_upstart_conf()

	def cleanup(self):
		
		for script in self.scripts.values():
			script.cleanup()
		self.ssh.close()

	def __str__(self):
		return self.address

	def load(self, path, name):

		if name in self.scripts:
			print("error: %s already loaded" % (name,))
			return

		script = BroScript(self, name, path, self.cur_bro_port)
		self.cur_bro_port += 1
		self.scripts[name] = script

		script.load()
		script.send()

	def run(self, name):

		if name not in self.scripts:
			print("error: unknown script '%s'" % (name,))
			return

		script = self.scripts[name]
		script.run()
		script.connect()

	def stop(self, name):

		if name not in self.scripts:
			print("error: unknown script '%s'" % (name,))
			return

		script = self.scripts[name]
		script.disconnect()
		script.stop()

	def install_upstart_conf(self):

		self.sftp.put(BroScript.UPSTART_CONF, "/etc/init/bro-yanc.conf")


class BroScript(object):

	MODULE_IN   = "lib/main.bro.in"
	LOAD_IN     = "lib/__load__.bro.in"
	REMOTE_PATH = "/usr/local/bro/share/bro/base/frameworks"
	UPSTART_CONF = "lib/upstart-bro-yanc.conf"

	def __init__(self, bro, name, local_script_path, port):

		self.bro  = bro
		self.ssh  = bro.ssh
		self.sftp = bro.sftp

		self.name = name
		self.port = port
		self.local_script_path  = local_script_path
		self.remote_script_path = "/run/" + name + ".bro"
		self.remote_mod_path    = BroScript.REMOTE_PATH + "/" + self.name

		self.cxn = None
		self.running = False
		self.polling_interval = 0.1

		self.int_cache    = dict()
		self.string_cache = dict()
		self.addr_cache   = dict()

		self.register_callbacks()

	def cleanup(self):
	
		self.disconnect()
		self.stop()
		self.purge()

	def load(self):

		with open(BroScript.LOAD_IN, "r") as fd:
			self.f_load = fd.read()

		with open(BroScript.MODULE_IN, "r") as fd:
			self.f_mod = fd.read()

		self.f_mod = re.sub("@MODULE_NAME@", self.name, self.f_mod)
		self.f_mod = re.sub("@LISTEN_PORT@", str(self.port), self.f_mod)
		self.f_mod = re.sub("@REMOTE_HOST@", "127.0.0.1", self.f_mod) #FIXME

		with open(self.local_script_path, "r") as fd:
			self.f_script = fd.read()

		self.f_script = re.sub("@MODULE_NAME@", self.name, self.f_script)

	def send(self):

		try:
			self.sftp.mkdir(self.remote_mod_path)
		except:
			pass
		self.sftp.chdir(self.remote_mod_path)

		with self.sftp.open("__load__.bro", "w") as fd:
			fd.write(self.f_load)
		with self.sftp.open("main.bro", "w") as fd:
			fd.write(self.f_mod)
		with self.sftp.open(self.remote_script_path, "w") as fd:
			fd.write(self.f_script)

	def purge(self):

		try:
			self.sftp.remove(self.remote_script_path)
		except Exception as e:
			print("warning: error removing '%s': %s" % (self.remote_script_path, str(e)))

		try:
			self.sftp.chdir(self.remote_mod_path)
		except Exception as e:
			print("warning: error changing to '%s': %s" % (self.remote_mod_path, str(e)))

		for f in self.sftp.listdir():
			try:
				self.sftp.remove(f)
			except Exception as e:
				print("warning: error removing '%s': %s" % (f, str(e)))

		self.sftp.chdir("..")
		try:
			self.sftp.rmdir(self.remote_mod_path)
		except Exception as e:
			print("warning: error removing '%s': %s" % (self.remote_mod_path, str(e)))

	def run(self):
		if self.running:
			print("warning: '%s' already running" % (self.name))
		else:
			self.ssh.exec_command("start bro-yanc id=" + self.name)
			self.running = True
			# Give the script a second listen on port
			time.sleep(1)

	def stop(self):
		if not self.running:
			print("warning: '%s' not running" % (self.name))
		else:
			self.ssh.exec_command("stop bro-yanc id=" + self.name)
			self.running = False

	def connect(self):
		if self.cxn:
			print("warning: '%s' already connected" % (self.name,))
		else:
			self.cxn    = broccoli.Connection(self.bro.hostname + ":" + str(self.port))
			self.run_thread = True
			self.thread = threading.Thread(target=self.poll, name="script:"+self.name)
			self.thread.daemon = True
			self.thread.start()


	def disconnect(self):
		if not self.cxn:
			print("warning: '%s' not connected" % (self.name,))
		else:
			self.run_thread = False
			self.thread.join()
			del self.thread
			del self.cxn
			self.cxn = None

	def poll(self):

		while self.run_thread:
			self.cxn.send("init_update")
			time.sleep(self.polling_interval)
			self.cxn.processInput()

	def set_string(self, key, val):
		self.cxn.send("set_string", key, val)

	def set_int(self, key, val):
		self.cxn.send("set_int", key, val)

	def set_addr(self, key, val):
		self.cxn.send("set_addr", key, val)

	def register_callbacks(self):
		@broccoli.event
		def update_strings(name, value):
			self.string_cache[name] = value

		@broccoli.event
		def update_addrs(name, value):
			self.addr_cache[name] = value

		@broccoli.event
		def update_ints(name, value):
			self.int_cache[name] = value


def parse_ssh_hostname(arg):

	user_hostport = arg.split('@', 1)

	if len(user_hostport) == 2:
		user      = user_hostport[0]
		hostport  = user_hostport[1]
	else:
		user      = None
		hostport  = user_hostport[0]

	host_port = hostport.split(':', 1)

	host = host_port[0]
	if len(host_port) == 2:
		port  = int(host_port[1])
	else:
		port  = None

	return host, user, port

def format_ssh_hostname(host, user=None, port=None):

	fmt = host
	if user is not None:
		fmt = user + "@" + fmt
	if port is not None:
		fmt = fmt + ":" + str(port)
	return fmt

if __name__ == "__main__":
	sh = BroShell()
	sh.cmdloop(USAGE)
	sh.cleanup()

# vim: set noet ts=8 sts=8 sw=0 :
