#!/usr/bin/env python

import os
import sys
import cgi
import re

print "Content-Type: text/HTML\n\n"
print """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>Ping Test Interface</title>
    <link rel="stylesheet" type="text/css" href="/styles.css" />
  </head>
  <body>
"""

form = cgi.FieldStorage()
if form.has_key('chkLink'):
	# performs a link up check
	linked = os.popen('sudo mii-tool').read()
	print "Link Status : "
	print linked
elif form.has_key('nsLookup'):
	# peforms a nslookup on comat.com
	print "NameServer Lookup (comat.com) "
	nsl = os.popen('nslookup comat.com').read()
	print "<pre>"
	print nsl
	print "</pre>"
elif form.has_key('pingGW'):
	# performs a ping test on the default gateway
	print "Ping Stats : "
	route = os.popen('route').read()
	defgw = re.search('default\s(?P<gw>.*)\s0.0.0.0',route).group('gw').strip()
	pingcmd = 'ping -c 3 '+defgw
	result = os.popen(pingcmd).read()
	print "<pre>"
	print result
	print "</pre>"
#	# find DNS
#	resolve = file('/etc/resolv.conf','r').read()
#	dnsip = re.search('nameserver\s(?P<ip>.*)',resolv).group('ip')
else:
	# print the form page
	print """
	<h1> Link-NSLookup-Ping Tests</h1>
	<form action="" method="post">
	<table id="clickping">
	<tr><th>Click for Link Status</th><td><input type="submit" name="chkLink" value="Check Link"</td></tr>
	<tr><th>Click for NSLookup</th><td><input type="submit" name="nsLookup" value="NS Lookup"</td></tr>
	<tr><th>Click for Ping Test</th><td><input type="submit" name="pingGW" value="Ping Now"</td></tr>
	</table></form>
	"""
print """
    </body>
</html>
"""
	
