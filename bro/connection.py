#!/usr/bin/env python2

import paramiko
from   bro.util  import *
from   bro.script import BroScript

class BroConnection(object):

	def __init__(self, alias, hostname, port=None, user=None):

		self.alias     = alias
		self.hostname  = hostname
		self.user      = user
		self.port      = port
		self.address   = format_ssh_hostname(hostname, user, port)

		self.log       = get_logger(self.alias)

		# An index of the currently loaded .bro scripts. 

		self.scripts   = dict()
		self.cur_bro_port = 47000

		# Establish SSH/SFTP tunnel to remote server

		kwargs = dict()
		if port is not None:
			kwargs["port"] = port
		if user is not None:
			kwargs["username"] = user

		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(hostname, **kwargs)
		self.sftp = self.ssh.open_sftp()

		# Manage the run-state of scripts via upstart

		self.install_upstart_conf()

	def cleanup(self):
		
		for script in self.scripts.values():
			script.cleanup()
		self.ssh.close()

	def __str__(self):
		return self.alias

	def load(self, path, name):

		if name in self.scripts:
			self.log.warning(str(name) + " already loaded")
			return

		script = BroScript(self, name, path, self.cur_bro_port)
		self.cur_bro_port += 1
		self.scripts[name] = script

		script.load()
		script.send()

	def run(self, name):

		if name not in self.scripts:
			self.log.warning("unknown script " + str(name))
			return

		script = self.scripts[name]
		script.run()
		script.connect()

	def stop(self, name):

		if name not in self.scripts:
			self.log.warning("unknown script " + str(name))
			return

		script = self.scripts[name]
		script.disconnect()
		script.stop()

	def install_upstart_conf(self):

		self.sftp.put(BroScript.UPSTART_CONF, "/etc/init/bro-yanc.conf")


# vim: set noet ts=8 sts=8 sw=0 :
# this is a test
