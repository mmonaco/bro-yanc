
#############################Load Frameworks#################################################
@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/yanc
@load base/frameworks/control

###########################################################################################

global update:event(a: string, b: addr);

event bro_init(){

	print "Minimal bro is up";

	yanc::addr_map["default"]=0.0.0.0;
	yanc::addr_map["a"]=99.99.99.99;
}

event bro_list(){
	#go through the users and print out users in the set on the bro device 
	for ( host in yanc::addr_map ){
        print fmt("On small script:  %s is mapped to %s", host,yanc::addr_map[host]);
	}
}

event bro_demo(){
	print fmt("BRO DEMO INTIATED!");
	print fmt("Blocking ip address on BRO1 is: %s", yanc::addr_map["a"]);
}