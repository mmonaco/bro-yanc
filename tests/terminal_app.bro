
#############################Load Frameworks#################################################
@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/yanc
@load base/frameworks/control

###########################################################################################

####################################For controlling the child script#####################################

redef Communication::nodes += {
["foo"] = [$host = 127.0.0.1, $p=1337/tcp, $events = /my_event_response/, $connect=T]
};

#this recieves the event 

event build_table_command()
{
#print "XXXXXXXXXXXXXXXXXXXXXXXsent build_table_command";
}

 
event remote_connection_handshake_done(p: event_peer) 
{
print fmt("@@@@@@@@@@@@@@@@@@@@connection established to: %s", p);
event build_table_command();
}



#######################Sets up connection with yanc controller#############################
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
        ["controller"] = [$host = 127.0.0.1, $events = /test1|setvar|list|init_update|bro_list/, $connect=F, $ssl=F] #declares the tests 
};
###########################################################################################


global update:event(a: string, b: addr);


event bro_init(){
	print "bro is up ";
}

event child_command(){

}
event test1(){
        print "bro completed task, move to test1"; 
}

event setvar(x:string, y:addr){

	print "Setvar ran";

	local bro_rec : yanc::ip_map;
	#sets up a record 
	  bro_rec$local_name = x;
	  #name 
	  bro_rec$ip = y;

	  #

	add yanc::user_set[bro_rec];
}
#bro list is for debugging purposes
event bro_list(){
	for ( b in yanc::user_set ) #go through the users and print out users in the set on the bro device 
        print fmt("  %s", b);
}

event init_update(){
	print "init_update";


	for ( b in yanc::user_set)
		#print fmt("  %s", b$local_name);
		#print fmt("  %s", b$ip);
		event update(b$local_name, b$ip);
		print "started update";
}