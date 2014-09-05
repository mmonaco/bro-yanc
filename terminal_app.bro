
#############################Load Frameworks#################################################
@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/yanc
@load base/frameworks/control

###########################################################################################
####################################For controlling the child script#####################################

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
        ["controller"] = [$host = 127.0.0.1, $events = /test1|setvar|list|init_update|bro_list|delvar/, $connect=F, $ssl=F] #declares the tests 
};
###########################################################################################

global update:event(a: string, b: addr);

event bro_init(){
	print "bro is up ";
}

event test1(){
        print "bro completed task, move to test1"; 
}

#This deletes a record from the host_set 
event delvar(local_name:string, ipAddress:addr){

	print "Delvar ran";

	local bro_rec : yanc::ip_map;
	#sets up a record 
	bro_rec$local_name = local_name;
	 #name 
	bro_rec$ip = ipAddress;

	delete yanc::host_set[bro_rec];
}

#This adds a record to the host set
event setvar(local_name:string, ipAddress:addr){

	print "Setvar ran";

	local bro_rec : yanc::ip_map;
	#sets up a record 
	bro_rec$local_name = local_name;
	 #name 
	bro_rec$ip = ipAddress;

	add yanc::host_set[bro_rec];
}

#bro list is for debugging purposes
event bro_list(){
	#go through the users and print out users in the set on the bro device 
	for ( host in yanc::host_set ){
        print fmt("  %s", host);
	}
}

#init update, loops through user set and sends the info to the python controlller 
event init_update(){
	for ( host in yanc::host_set){
		event update(host$local_name, host$ip);
	}
}
