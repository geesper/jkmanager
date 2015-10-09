#!/usr/bin/python
import os
from jkmanager import *

try:
  passed_url = sys.argv[1]
except:
  print "No url was passed! Provide a url: http://servername/jkmanager"
  quit()

username = ''
password = ''
parser = JKManager(passed_url)
parser.set_credentials(username, password)
parser.run()

quit = False
while quit == False:
   print "\n======================="
   print "Current status: (" + str(len(parser.servers)) + " node(s) found)"
   print "=======================\n"
   print "Status     Server               Worker\tBalancer"
   for instance in parser.servers:
      server_status = instance.getStatus()
      server_name = (instance.vahst).split(".")[0]
      if (server_status == "Active"):
         print "[\033[92m Active \033[0m] " + server_name + "\t" + instance.name + "\t" + instance.balancer
      elif (server_status == "Disabled"):
         print "[\033[31mDisabled\033[0m] " + server_name + "\t" + instance.name + "\t" + instance.balancer
   print
   input = raw_input("Status, Enable, Disable: ")
   if input.lower() == "enable":
      for server in parser.servers:
        server.enable()
   elif input.lower() == "disable":
      print "Disabling..."
      for server in parser.servers:
        server.disable()
   elif input.lower() == "quit":
      quit = True

