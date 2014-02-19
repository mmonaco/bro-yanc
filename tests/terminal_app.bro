@load frameworks/communication/listen #this sets up the bro framework 
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
        ["broping"] = [$host = 127.0.0.1, $events = /test1|setvar|list|init_update|bro_list/, $connect=F, $ssl=F] #declares the tests 
};

type rec: record {
 #this intializes a data struct for us to use with the with setbro
    local_name: string;
    cont_name: string;
};

global broblematic_users:set[rec]; 

global update: event(a: string, b: string);

event bro_init(){
print "bro is up ";
}

event test1(){
        print "bro completed task, move to test1"; 
}

event setvar(x:string, y:string){

	print "Setvar ran";

	local bro_rec : rec;
	  bro_rec$local_name = x;
	  bro_rec$cont_name = y;

	add broblematic_users[bro_rec];
}
#bro list is for debugging purposes
event bro_list(){
	for ( b in broblematic_users ) #go through the users and print out users in the set on the bro device 
        print fmt("  %s", b);
}

event init_update(){
	print "init_update";
	for ( b in broblematic_users)
		#print fmt("  %s", b$local_name);
		#print fmt("  %s", b$cont_name);
		event update(b$local_name, b$cont_name);
		print "started update";
}