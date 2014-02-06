@load frameworks/communication/listen
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
	["broping"] = [$host = 127.0.0.1, $events = /test1|test2|test3/, $connect=F, $ssl=F]
};
global test2: event(a: int, b: count, c: time, d: interval, e: bool, f: double, g: string, h: port, i: addr, j: subnet, i6: addr, j6: subnet);

event test1(a: int, b: count, c: time, d: interval, e: bool, f: double, g: string, h: port, i: addr, j: subnet, i6: addr, j6: subnet)
{
    print "==== atomic";
    print a;
    print b;
    print c;
    print d;
    print e;
    print f;
    print g;
    print h;
    print i;
    print i6;
    print j;
    print j6;
    
    event test2(-4, 42, current_time(), 1min, T, 3.14, "Hurz", 12345/udp, 1.2.3.4, 22.33.44.0/24, [2607:f8b0:4009:802::1014], [2607:f8b0:4009:802::1014]/32);
    event test2(a,b,c,d,e,f,g,h,i,j,i6,j6);
    print "Hello World";
}
