bro-yanc
========

Bro module for yanc sdn controller. 

Installation
============
To get started download and install a copy of bro 2.2 or greater and the Broccoli python library to your computer. Information for how to do this is here:https://www.bro.org/sphinx/components/broccoli/README.html

Running bro-yanc
================
To run and test bro-yanc, start the bro script terminal_app.bro and terminal_appy.py. To start connecting, type:

```> connect bro1```

This will create a connection between your client and bro1. This is a shortcut command for testing purposes and creates a connection to ```127.0.0.1:47758```. You can then set varaibles using the command ```setvar```(ex. ```setvar a 1.1.1.1```) , which would create a connection in the bro module between a and 1.1.1.1, you can delete them with ```delvar```(ex. ```delvar a 1.1.1.1```) which would delete the variable. You can also run ```ls_var``` which will order the bro device to dump all of it's variable maps (ex. a:1.1.1.1, b:2.2.2.2, c:3.3.3.3) to the controller and then display them. 

