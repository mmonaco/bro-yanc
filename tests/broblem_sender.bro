@load frameworks/communication/listen #this sets up the bro framework 
redef Communication::listen_port = 47758/tcp;

redef Communication::nodes += {
        ["broping"] = [$host = 127.0.0.1, $events = /test1|test2/, $connect=F, $ssl=F] #declares the tests 
};


#############################################################

global broblematic_users: set[addr]; #creates the set of users that we will work with 


event test1(i:addr)
{
        #print "This is alex's test";
        add broblematic_users[i]; #adds each user to the set #add the users to a list 
}
#TODO pipe arrays into bro so it can add whole arrays as opposed to individual users. 

event test2()
        {
        print "The following users might be experiencing  Broblems:"; 
        for ( b in broblematic_users ) #go through the users and print out users in the set
                print fmt("  %s", b);
        }

#TODO figure out how to auto-quit program at the end ls