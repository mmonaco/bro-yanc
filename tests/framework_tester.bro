@load base/frameworks/yanc

event bro_init(){

	local table_test = global_ids();

	for (k in table_test){
		local temp = table_test[k];
		#if (temp$exported == F && temp$constant == F && temp$redefinable == F){
			print k;
			print temp;
		#
	}
	print "bro is up ";
	for ( b in yanc::user_set){
		print "done";
		print (b$local_name);
		print (b$ip);

	};
	print "shit";
}
