bro-yanc
========

Bro module for yanc sdn controller. Any line in the format ```>>...``` means it is a command to be typed into the controller end. 

Installation
============
To get started download and install a copy of bro 2.2 or greater and the Broccoli python library to your computer. Information for how to do this is here:https://www.bro.org/sphinx/components/broccoli/README.html

General Test
===============
1.  Create a sample bro script, in this case we are using the sample_script.bro. This script has an event, bro_demo, which will print out a variable map on the bro device. 

2.  While writing the bro script, instead of using normal variables make it yanc::addr_map["x"] for addresses. So instead of making a variable ```count=5``` you would write ```yanc::int_map["count"]``` and ```yanc::int_map["b"]=55``` in the bro_int porition of the script. 

3.  Create a custom module using do_create_module and modify a script to take the new module. This takes the template yanc/main.bro, copies it and replaces the name and port with our parameters. Use the command ```>> module smiley  1337/tcp 127.0.0.5 sample_script.bro ``` in terminal_app.py to create the custom module. Put the new directory in /usr/local/bro/share/bro/base/frameworks/. This also yancifies a script so it can work with the new module. 

4. NOW DONE IN MODULE MAKER. DEPRICATED! do_create_module "yancify" the script using the do_modify_script. This takes in a bro file name that we want to modify, and the module name of the module we created in step three. Example: ```>> modify_script sample_script.bro test_mod``` 

5.  Send the script to proper directory on the device. Still working on this, for now you can jsut run the script directly using your bro commands. 

7.  Run the bro script and start changing vars from the controllers terminal_app.py

Notes: All of the connections between the controller and the bro device are kept in custom module, so when the script is being written the only thing the writer needs to worry about is making the variables look at the different table maps, which can use the placeholder value of ```yanc::___int_map[]``` because our script modifer will change the actual module name and any references.

Connections with bro-yanc
=========================
To run and test bro-yanc, start the bro script terminal_app.bro and terminal_appy.py. To start connecting, type:

```>> connect 127.0.0.1:47758 bro1```

This will create a connection between your client and the bro device that we will refer to as bro1. If the module was created properly with the same ip address, it should be listening @ 127.0.0.1 on port 47758.

If you are maintaining more than one connection, you can use the command: 
```>> connections ```
to list open connections. Also the command:
```>> current_connection```
will list the bro device that we are currently interacting with. 

The way the code is setup, is that you are interfacing with only one bro device at a time, so the variable dictionary is tied directly to that bro device. 

Setting Variables
=================
To actually change variables on the bro end of a device. Make sure you are connected properly. To get a list of varaibles that have been set already use the command ```>> ls_var``` this will contact the bro instace and retrieve a list of variables and maps. From there, you can set different variables depending on data type. For example, we might use the command ```>> set_int b 45``` to set the variable c to 45 on the bro end. Or we might use ```>> set_addr a 192.168.1.1``` to set the address for variable d. We can also use ```>> set_string c foobar``` to change the map of b to a string "foobar". You can test these by calling ```>> demo``` when working with the sample_script. 



