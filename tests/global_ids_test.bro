@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/yanc
 
redef Communication::listen_port = 1337/tcp;
 
redef Communication::nodes += {
["foo"] = [$host = 127.0.0.1, $events = /my_event_request/, $connect = F]
};
 
event remote_connection_handshake_done(p: event_peer)
{
	print fmt("connection established to: %s", p);
}
 
global request_count: count = 0;
 
event my_event_response(details: count)
{
	print "sent my_event_response", details;
}
 
event my_event_request(details: string)
{
	local table_test = global_ids();

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
	#print "recv my_event_request", details;
	++request_count;
	event my_event_response(request_count);
}
 
event remote_connection_closed(p: event_peer)
{	
	print fmt("connection to peer closed: %s", p);
}



##################################################################



global hello: string "hello world";
global james: addr 192.23.1.233;
global test: port 80/tcp;
global bob: string "jkhsdfjkhsdkjhsdjkhlf";
global ram: int 5;

event bro_init(){
	local hi = "I'm a local string";
	
}	



event build_table(){

	local table_test = global_ids();

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

