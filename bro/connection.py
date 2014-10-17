#!/usr/bin/env python2

from __future__ import print_function
import paramiko
from   bro.util  import *
from   bro.script import BroScript

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


# vim: set noet ts=8 sts=8 sw=0 :
# this is a test