#!/usr/bin/env python2

from bro.shell import BroShell, USAGE

if __name__ == "__main__":
	sh = BroShell()
	sh.cmdloop(USAGE)
	sh.cleanup()

# vim: set noet ts=8 sts=8 sw=0 :
