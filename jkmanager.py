#!/usr/bin/python

import os
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import urllib2
import base64
import getpass
import socket


# This class handles the generic jkstatus page. It pulls the data from there, populating "servers" with an array of "Server" objects. Each Server object refers to a server that appears on the jkmanager page.
class JKServerManager(HTMLParser):
    def __init__(self, url, username, password):
        HTMLParser.__init__(self)
        self.inLink = False
        self.inH3 = False
        self.lasttag = None
        self.servers = []
        self.balancer = ""
        self.base_balancer_url = url
        self.username = username
        self.password = password
        self.feed(jkmanager_get_html(self.base_balancer_url, self.username, self.password))

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
           self.inH3 = True
           self.lasttag = tag
        if tag == 'a':
           self.inLink = True
           for attr in attrs:
              if ("?cmd=edit&from=list&w=" + self.balancer + "&sw=") in attr[1]:
                 tempname = attr[1].split('&sw=')[1] # grabbing the name
                 tempurl = attr[1].split('?')[1]
                 tempurl = self.base_balancer_url + "?" + tempurl
                 temp2 = Server(tempname, self.balancer, tempurl, self.base_balancer_url, self.username, self.password)
                 self.servers.append(temp2)

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.inH3 = False
            self.lasttag = tag
        if tag == 'a':
            self.inLink = False

    def handle_data(self, data):
        if self.inH3 == True:
           if "Worker Status for" in data:
               temparray = data.split(" ")
               self.balancer = temparray[len(temparray) - 1]
              
              
# This parser reads the jkmanager edit page and is used by the Server object to populate settings it has.                
class JKServerEdit(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.inLink = False
        self.inTD = False
        self.TD = None
        self.status = None
        self.lasttag = None
        self.servers = []
        self.balancer = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
           self.inTD = True
           self.lasttag = tag
        if tag == 'input':
           tempname = None
           tempvalue = ''
           for attr in attrs:
              if attr[0] == 'checked':
                 self.status = self.TD
                 if self.TD == "Active":
                    self.vwa = '0'
                 elif self.TD == "Disabled":
                    self.vwa = '1'
                 elif self.TD == "Stopped":
                    self.vwa = '2'	  
              if attr[0] == 'name':
                 tempname = attr[1]
              if attr[0] == 'value':
                 tempvalue = attr[1]
           if tempname == 'vwf':
              self.vwf = tempvalue
           if tempname == 'vwn':
              self.vwn = tempvalue
           if tempname == 'vwr':
              self.vwr = tempvalue
           if tempname == 'vwc':
              self.vwc = tempvalue
           if tempname == 'vwd':
              self.vwd = tempvalue
           if tempname == 'vahst':
              self.vahst = tempvalue
           if tempname == 'vaprt':
              self.vaprt = tempvalue
           if tempname == 'vacpt':
              self.vacpt = tempvalue
           if tempname == 'vapng':
              self.vapng = tempvalue
           if tempname == 'vact':
              self.vact = tempvalue
           if tempname == 'vapt':
              self.vapt = tempvalue
           if tempname == 'vart':
              self.vart = tempvalue
           if tempname == 'var':
              self.var = tempvalue
           if tempname == 'vari':
              self.vari = tempvalue
           if tempname == 'vacpi':
              self.vacpi = tempvalue
           if tempname == 'varo':
              self.varo = tempvalue
           if tempname == 'vamps':
              self.vamps = tempvalue

    def handle_endtag(self, tag):
        if tag == 'td':
            self.inTD = False
            self.lasttag = tag

    def handle_data(self, data):
        if self.inTD == True:
           self.TD = data


# This class handles placing/removing a server in rotation.
class Server():
   def __init__(self, node_name, balancer, editURL, url, username, password):
      self.node_name = node_name
      self.balancer = balancer
      self.editURL =  editURL
      self.status = None
      self.base_balancer_url = url
      self.username = username
      self.password = password
   def getStatus(self):
      if self.status == None:
         tempparser = JKServerEdit()
         tempparser.feed(jkmanager_get_html(self.editURL, self.username, self.password))
         self.status = tempparser.status
         self.vwa = tempparser.vwa
         self.vwf = tempparser.vwf
         self.vwn = tempparser.vwn
         self.vwr = tempparser.vwr
         self.vwc = tempparser.vwc
         self.vwd = tempparser.vwd
         self.vahst = tempparser.vahst
         self.vaprt = tempparser.vaprt
         self.vacpt = tempparser.vacpt
         self.vapng = tempparser.vapng
         self.vact = tempparser.vact
         self.vapt = tempparser.vapt
         self.vart = tempparser.vart
         self.var = tempparser.var
         self.vari = tempparser.vari
         self.vacpi = tempparser.vacpi
         self.varo = tempparser.varo
         self.vamps = tempparser.vamps
         self.server_name = (self.vahst).split(".")[0]
      return self.status
   def __setStatus(self, value):
      if self.status == None:
         temp = self.getStatus()
      tempURL = self.base_balancer_url + "?cmd=update&from=list&w=" + self.balancer + \
      "&sw=" + self.node_name + \
      "&vwa=" + value + \
      "&vwf=" + self.vwf + \
      "&vwn=" + self.vwn + \
      "&vwr=" + self.vwr + \
      "&vwc=" + self.vwc + \
      "&vwd=" + self.vwd + \
      "&vahst=" + self.vahst + \
      "&vaprt=" + self.vaprt + \
      "&vacpt=" + self.vacpt + \
      "&vapng=" + self.vapng + \
      "&vact=" + self.vact + \
      "&vapt=" + self.vapt + \
      "&vart=" + self.vart + \
      "&var=" + self.var + \
      "&vari=" + self.vari + \
      "&vacpi=" + self.vacpi + \
      "&varo=" + self.varo + \
      "&vamps=" + self.vamps
      temp = jkmanager_get_html(tempURL, self.username, self.password)
      self.status = None
   def disable(self):
      self.__setStatus("1")
   def enable(self):
      self.__setStatus("0")
   def stop(self):
      self.__setStatus("2")

# This function is used to pull the html from the url using the username/password provided. It returns the raw HTML, which can be fed to the above.
def jkmanager_get_html(url, username, password, recursion = False):
   socket.setdefaulttimeout(.5)
   request = urllib2.Request(url)
   base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
   request.add_header("Authorization", "Basic %s" % base64string)
   try:   
      result = urllib2.urlopen(request,timeout=None)
      data = result.read()
      result.fp._sock.recv=None
      return data 
   except Exception,e:
         print "Error opening url (" + url + "): " + str(e) 
         return ""

class JKManager():
	def __init__(self, url):
		self.url = url
		self.username = ""
		self.password = ""
		
	def set_credentials(self, username, password):
		self.username = username
		self.password = password
	
	def run(self):
		self.jk = JKServerManager(self.url, self.username, self.password)

