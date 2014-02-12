@load frameworks/communication/listen #this sets up the bro framework 
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
        ["broping"] = [$host = 127.0.0.1, $events = /test1|setvar|update|list/, $connect=F, $ssl=F] #declares the tests 
};

type rec: record { #this intializes a data struct for us to use with the with setbro
    local_name: string;
    cont_name: string;
};

global broblematic_users: set[rec]; 

event bro_init(){
print "bro is up ";
}

event test1(){
        print "bro completed task, move to test1"; 
}

event setvar(x:string, y:string){
	print "We recieved it";
	print fmt("  %s", x);
	print fmt("  %s", y);

	local sample : rec;
	  sample$local_name = x;
	  sample$cont_name = y;

	add broblematic_users[sample];
	for ( b in broblematic_users ) #go through the users and print out users in the set
        print fmt("  %s", b);
	#create global record with x,y

};

