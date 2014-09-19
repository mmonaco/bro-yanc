
#############################Load Frameworks#################################################
@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/@MODULE_NAME@
@load base/frameworks/control

###########################################################################################

event bro_init(){

	print "Sample_script bro is up";

	@MODULE_NAME@::addr_map["a"]=99.99.99.99;
	@MODULE_NAME@::int_map["b"]=55;
	@MODULE_NAME@::string_map["c"]="test";

}

event bro_list(){
	#go through the users and print out users in the set on the bro device 
	for ( host in @MODULE_NAME@::addr_map ){
        print fmt("On small script:  %s is mapped to %s", host,@MODULE_NAME@::addr_map[host]);
	}
}

event bro_demo(){
	print fmt("BRO DEMO INTIATED!");
	print fmt("Address is: %s", @MODULE_NAME@::addr_map["a"]);
	print fmt("Integer map is: %s", @MODULE_NAME@::int_map["b"]);
	print fmt("String is: %s", @MODULE_NAME@::string_map["c"]);


}
