
#############################Load Frameworks#################################################
@load frameworks/communication/listen #this sets up the bro framework for listening from python 
@load base/frameworks/communication
@load base/frameworks/yanc
@load base/frameworks/control

###########################################################################################

global update:event(a: string, b: addr);

event bro_init(){
	print "bro is up ";

	local bro_rec : yanc::ip_map;

	bro_rec$local_name = "default";
	bro_rec$ip = 0.0.0.0;

	add yanc::host_set[bro_rec];
}
