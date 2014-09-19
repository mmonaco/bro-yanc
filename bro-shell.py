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

class BroScript(object):

	MODULE_IN   = "lib/main.bro.in"
	LOAD_IN     = "lib/__load__.bro.in"
	REMOTE_PATH = "/usr/local/bro/share/bro/base/frameworks"
	UPSTART_CONF = "lib/upstart-bro-yanc.conf"

	def __init__(self, ssh, sftp, name, local_script_path, port):

		self.ssh  = ssh
		self.sftp = sftp

		self.name = name
		self.port = port
		self.local_script_path  = local_script_path
		self.remote_script_path = "/run/" + name + ".bro"
		self.remote_mod_path    = BroScript.REMOTE_PATH + "/" + self.name

		self.cxn = None

	def __del__(self):

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

		self.sftp.mkdir(self.remote_mod_path)
		self.sftp.chdir(self.remote_mod_path)

		with self.sftp.open("__load__.bro", "w") as fd:
			fd.write(self.f_load)
		with self.sftp.open("main.bro", "w") as fd:
			fd.write(self.f_mod)
		with self.sftp.open(self.remote_script_path, "w") as fd:
			fd.write(self.f_script)

	def run(self):
		self.ssh.exec_command("start bro-yanc id=" + self.name)

	def stop(self):
		self.ssh.exec_command("stop bro-yanc id=" + self.name)


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

	def __str__(self):
		return self.address

	def load(self, path, name):

		if name in self.scripts:
			print("error: %s already loaded" % (name,))
			return

		script = BroScript(self.ssh, self.sftp, name, path, self.cur_bro_port)
		script.load()
		script.send()
		script.run()

		self.scripts[name] = script
		self.cur_bro_port += 1

	def install_upstart_conf(self):

		self.sftp.put(BroScript.UPSTART_CONF, "/etc/init/bro-yanc.conf")

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

	def __del__(self):
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


	def do_EOF(self, line):
		print()

	def postcmd(self, stop, line):
		if line == "EOF":
			return True

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
	BroShell().cmdloop()

# vim: set noet ts=8 sts=8 sw=0 :
