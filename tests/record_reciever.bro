
@load frameworks/communication/listen
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
	["broping"] = [$host = 127.0.0.1, $events = /test1|test3|test5/, $connect=F, $ssl=F] 
	#we only need the nests liststed that are sending. 
};

global test2: event(a: int, b: count, c: time, d: interval, e: bool, f: double, g: string, h: port, i: addr, j: subnet, i6: addr, j6: subnet);

event test1()

{

   event test2(-4, 42, current_time(), 1min, T, 3.14, "Keller", 12345/udp, 1.2.3.4, 22.33.44.0/24, [2607:f8b0:4009:802::1014], [2607:f8b0:4009:802::1014]/32);
   #test 1 initates test2, which will send the info back to the reciver python

}





