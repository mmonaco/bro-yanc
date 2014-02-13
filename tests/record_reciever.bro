
@load frameworks/communication/listen
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
	["broping"] = [$host = 127.0.0.1, $events = /init_update|test3|test5/, $connect=F, $ssl=F] 
	#we only need the nests liststed that are sending. 
};

global update: event(a: string, b: string);
event init_update()

{

   event update("john","bob");
   #test 1 initates update, which will send the info back to the reciver python

}





