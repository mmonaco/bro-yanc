#!/usr/bin/env python2

from __future__ import print_function

import sys
sys.path.append("/usr/local/bro/lib/broctl/")

import broccoli
import re
import time
import threading

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
		self.string_cache[key] = val

	def set_int(self, key, val):
		self.cxn.send("set_int", key, val)
		self.int_cache[key] = val

	def set_addr(self, key, val):
		self.cxn.send("set_addr", key, val)
		self.addr_cache[key] = val

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

# vim: set noet ts=8 sts=8 sw=0 :
