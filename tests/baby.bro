#@load frameworks/communication/listen #this sets up the bro framework for listening from python 
#@load base/frameworks/control #this is for controlling 
#@load base/frameworks/communication


#redef Communication::listen_port = 47758/tcp;
@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication

module Control;

redef Communication::listen_port = 4775/tcp;

redef Communication::nodes += {
        ["broping"] = [$host = 127.0.0.1, $events = /test1|setvar|list|init_update|bro_list/, $connect=F, $ssl=F] #declares the tests 
};

global hello: string "hello world";
global james: addr 192.23.1.233;
global test: string "jkhsdfjkhsdkjhsdjkhlf";
global bob: string "jkhsdfjkhsdkjhsdjkhlf";
global ram: int 5;

event bro_init(){
	local hi = "I'm a local string";
	#print hello;
	#print hi;
	local table_test = global_ids();
	local test_rec = table_test["Control::james"];
	#print test_rec$value;
	for (k in table_test){
		local temp = table_test[k];
		if (temp$exported == F && temp$constant == F && temp$redefinable == F){
			print k;
			print temp;
		}
	}
	print hi;
}