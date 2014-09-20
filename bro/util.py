#!/usr/bin/env python2

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


# vim: set noet ts=8 sts=8 sw=0 :
