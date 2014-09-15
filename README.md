bro-yanc
========

Bro module for yanc sdn controller. 

Installation
============
To get started download and install a copy of bro 2.2 or greater and the Broccoli python library to your computer. Information for how to do this is here:https://www.bro.org/sphinx/components/broccoli/README.html

General Outline
===============
Proper way to use the program: 
1. Create a sample bro script. 
2. While writing the bro script, instead of using normal variables make it yanc::user_set[x](finishing this up)
3. Create a custom module using do_create_module
4. "yancify" the script using the do_modify_script
5. Send the script to proper directory on the device
6. Send the module to the frameworks directory 
7. Run the bro script and start changing stuff from the controllers terminal_app.py

Notes- All of the connections between the controller and the bro device are kept in custom module, so when the script is being written the only thing the writer needs to worry about is making the variables look at the module, which can use the placeholder value of yanc:: because our script modifer will change the actual module name and any references.

Running bro-yanc
================
To run and test bro-yanc, start the bro script terminal_app.bro and terminal_appy.py. To start connecting, type:

```> connect bro1```

This will create a connection between your client and bro1. This is a shortcut command for testing purposes and creates a connection to ```127.0.0.1:47758```. You can then set varaibles using the command ```setvar```(ex. ```setvar a 1.1.1.1```) , which would create a connection in the bro module between a and 1.1.1.1, you can delete them with ```delvar```(ex. ```delvar a 1.1.1.1```) which would delete the variable. You can also run ```ls_var``` which will order the bro device to dump all of it's variable maps (ex. a:1.1.1.1, b:2.2.2.2, c:3.3.3.3) to the controller and then display them. 




