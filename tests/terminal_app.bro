@load frameworks/communication/listen #this sets up the bro framework 
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
        ["broping"] = [$host = 127.0.0.1, $events = /test1|setvar|update|list/, $connect=F, $ssl=F] #declares the tests 
};

type var: record { #this intializes a data struct for us to use with the with setbro
    a: string;
    b: addr;
};

event bro_init(){
print "bro is up ";
}

event test1(){
        print "test1/bro is ready to recieve"; 
}

event setvar(x:string, y:addr){
	print "We recieved it";
	print fmt("  %s", x);
	print fmt("  %s", y);
	#create global record with x,y

};

