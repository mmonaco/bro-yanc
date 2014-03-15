global counter = 0; 

event bro_init(){
	print("Test a is working!")
}

event yahoo_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string)
	{
	if ( "yahoo.com" in original_URI )
		counter+= 1; 
	}
