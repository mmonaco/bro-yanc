bro-yanc
========

Bro module for yanc sdn controller. 

Installation
============
To get started download and install a copy of bro 2.2 or greater and the Broccoli python library to your computer. Information for how to do this is here:https://www.bro.org/sphinx/components/broccoli/README.html

General Test
===============
1.  Create a sample bro script, in this case we are using the sample_script.bro. This script has an event, bro_demo, which will print out a variable map on the bro device. 

2.  While writing the bro script, instead of using normal variables make it yanc::addr_map["x"] for addresses. So instead of making a variable ```count=5``` you would write ```yanc::int_map["count"]``` and ```yanc::int_map["b"]=55``` in the bro_int porition of the script. 

3.  Create a custom module using do_create_module. This takes the template yanc/main.bro, copies it and replaces the name and port with our parameters. Use the command ```>> module test_mod 1337``` in terminal_app.py to create the custom module. Put the new directory in /usr/local/bro/share/bro/base/frameworks/ .

4.  "yancify" the script using the do_modify_script. This takes in a bro file name that we want to modify, and the module name of the module we created in step three. Example: ```modify_script sample_script.bro test_mod``` 

5.  Send the script to proper directory on the device. Still working on this, for now you can jsut run the script directly using your bro commands. 

7.  Run the bro script and start changing vars from the controllers terminal_app.py

Notes- All of the connections between the controller and the bro device are kept in custom module, so when the script is being written the only thing the writer needs to worry about is making the variables look at the different table maps, which can use the placeholder value of ```yanc::___map[]``` because our script modifer will change the actual module name and any references.

Connections with bro-yanc
=========================
To run and test bro-yanc, start the bro script terminal_app.bro and terminal_appy.py. To start connecting, type:

```>> connect 127.0.0.1:47758 bro1```

This will create a connection between your client and the bro device that we will refer to as bro1. If the module was created properly with the same ip address, it should be listening @ 127.0.0.1 on port 47758.

If you are maintaining more than one connection, you can use the command: 
```
>> connections 
```
to list open connections. Also the command:
```
>> current_connection
```
will list the bro device that we are currently interacting with. 



