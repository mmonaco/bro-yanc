@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/yanc
 

redef Communication::listen_port = 1337/tcp;
 #port to take orders from 

redef Communication::nodes += {
["foo"] = [$host = 127.0.0.1, $events = /build_table_command/, $connect = F]
#this is the master node, we need to edit this 
};

##################################################################
module yanc_id;

global hello: string "hello world";
global james: addr 192.23.1.233;
global test: port 80/tcp;
global bob: string "jkhsdfjkhsdkjhsdjkhlf";
global ram: int 5;

event bro_init(){
	local hi = "I'm a local string";
	
}	

event build_table(){

	print("I WAS CALLED");

	local table_test = global_ids();
	local finished_table;

	for (k in table_test){
		local temp = table_test[k];
		#very ugly hack. since all of the global variables declared in this file begin with "yanc_id", check to see if the 0th char = y and if the 4th char = "_"
		#This should be good enough for now, as long as there isn't anything of similar format. IF there is we can add more if conditions 
		if (k[0] == "y" && k[4] == "_" ){
		#make temp into a string and 
			print k;
			print temp;
		}
	}
}
####################################################################

event remote_connection_handshake_done(p: event_peer)
{
	print fmt("AAAAAAAAAAAAAAAAAAAAAAAAconnection established to: %s", p);
}
  
event send_ids()
event build_table_command()
{
	event build_table();
}
 
event remote_connection_closed(p: event_peer)
{	
	print fmt("connection to peer closed: %s", p);
}

