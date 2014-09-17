##! This is our bro framework

module yanc;

export {
	#we can add a new map for every type of variable
	global addr_map:	table[string] of addr;
	global int_map:		table[string] of int;
	global string_map:	table[string] of string;
}

event my_event_request(details: string)
{
	print "sent my_event_request", details;
}
 
event my_event_response(details: count)
{
	print "recv my_event_response", details;
	print "terminating";
	terminate();
}
 
#This is run whenever an event is sent via bro 
event remote_connection_handshake_done(p: event_peer)
{
	#print fmt("connection established to: %s", p);
	event my_event_request("hello");
}

#######################Sets up connection with yanc controller#############################
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
        ["controller"] = [$host = 127.0.0.1, $events = /test1|set_string|list|init_update|bro_list|delvar|bro_demo|set_int|set_addr/, $connect=F, $ssl=F] #declares the tests 
};
###########################################################################################

global update_addrs:event(a: string, b: addr);
global update_strings:event(a: string, b: string);
global update_ints:event(a: string, b: int);

event bro_init(){
	print "YANC MODULE IS UP ";
	#this initializes some defaults to the variable tables
	yanc::addr_map["default_addr"]=0.0.0.0;
	yanc::int_map["default_int"]=0;
	yanc::string_map["default_string"]="null";
}

event test1(){
        print "bro completed task, move to test1"; 
}

#This deletes an entry from the addr_map, possibly need to add more.
event delvar(local_name:string){
	print "Delvar ran";
	delete addr_map[local_name];
}

#This adds a record to the host set
event set_addr(local_name:string, IpAddress:addr){
	print "Setaddr ran";
	delete addr_map[local_name];
	addr_map[local_name]=IpAddress;
}

event set_int(local_name:string, Int:int){
	print "Setint ran";
	delete int_map[local_name];
	int_map[local_name]=Int;
}

event set_string(local_name:string, String:string){
	print "Setstring ran";
	delete string_map[local_name];
	string_map[local_name]=String;
}

#bro list is for debugging purposes
event bro_list(){
	#go through the users and print out users in the set on the bro device 
	for ( address in addr_map ){
        print fmt("Variable is: %s, value is %s", address, addr_map[address]);
	}
}

#init update, loops through user set and sends the info to the python controlller 
event init_update(){

	for ( variable in addr_map){
		event update_addrs(variable, addr_map[variable]);
	}

	for ( variable in string_map){
		event update_strings(variable, string_map[variable]);
	}

	for ( variable in int_map){
		event update_ints(variable, int_map[variable]);
	}
}
