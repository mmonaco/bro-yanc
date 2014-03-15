global counter = 0; 

event bro_init(){
	print("Test a is working!")
}

event google_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string)
	{
	if ( "google.com" in original_URI )
		counter+= 1; 
	}
