#!/usr/bin/env python

import os
import sys
import cgi
import re
import netiface

print "Content-Type: text/html"
print # End of headers
print """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>IP Configuration</title>
    <link rel="stylesheet" type="text/css" href="/styles.css" />
"""

print "<!-- Reading system configuration -->"
hostname = file('/etc/hostname', 'r').read().strip()
iface = netiface.readInterface("/etc/network/interfaces", "eth0")
nameservers = netiface.readNameServers()
print "<!-- Done -->"

form = cgi.FieldStorage()
if form.has_key('submit'):
    print """
  </head>
  <body>
"""
    # Modify code comes here
    # Step 1: Update IP config
    # Step 2: Update resolv.conf if not dhcp
    # Step 3: Update hostname in /etc/hostname and /etc/hosts
    # Step 4: Restart networking.
    # XXX Alert! Potential severe security hole here. Parameters must be validated first.
    parameters = ['/usr/bin/sudo', '/usr/sbin/rbc_ipconfig_reconfigure', '--restart', '--iftype', form['iftype'].value, '--address', form['ipaddr'].value, '--netmask', form['netmask'].value, '--gateway', form['gateway'].value, '--hostname', form['hostname'].value, '--ifd', '/etc/network/interfaces.d']
    for nameserver in form['nameservers'].value.replace('\r', '').split('\n'):
        parameters.extend(['-d', nameserver])
    #reconfig_command = "sudo /usr/sbin/rbc_ipconfig_reconfigure --iftype '%s' -a '%s' -n '%s' -g '%s' --hostname '%s' %s" \
    #% (form['iftype'].value, form['ipaddr'].value, form['netmask'].value, form['gateway'].value, form['hostname'].value, ' '.join(form['nameservers'].value.replace('\r', '').split('\n')))
    #os.system(reconfig_command)
    os.spawnv(os.P_WAIT, '/usr/bin/sudo', parameters)
# # Status message display comes here
    print "<p>IP settings successfully saved.</p>"
    print "<p><small>Hostname change will become effective after the system is restarted.</small></p>"
    print "</body></html>"
else:
    # Display form to user.
    print """
  </head>
  <body>
    <h1>IP Configuration</h1>
    <form action="" method="post">
    <p>Current configuration:</p>
    <pre>%s
    </pre>""" % cgi.escape(iface.render())
    print """<p>Current network status</p><pre>
    %s</pre>""" % cgi.escape(os.popen('ifconfig eth0').read())
    print """
    <h2>New Configuration</h2>
    <p><label for="hostname">Hostname</label>
      <input type="text" name="hostname" id="hostname" value="%s" />
    </p>
    <p>IP Assignment:
    <input type="radio" name="iftype" value="dhcp" id="iftype-dhcp" %s>
    <label for="iftype-dhcp">Automatic (DHCP)</label> 
    <input type="radio" name="iftype" value="static" id="iftype-static" %s>
    <label for="iftype-static">Static</label></p>
    """ % (hostname,
           iface.iftype == "dhcp" and 'checked="checked" /' or ' /',
           iface.iftype == "static" and 'checked="checked" /' or ' /')
    print """
	<table id="static-details">
	<tr><th>IP Address</th><td><input type="text" name="ipaddr" value="%s"></td></tr>
	<tr><th>Netmask</th><td><input type="text" name="netmask" value="%s"></td></tr>
	<tr><th>Gateway</th><td><input type="text" name="gateway" value="%s"></td></tr>
    <tr><th>DNS Servers</th><td><textarea name="nameservers">%s</textarea></td></tr>
	</table>
    """ % (iface.ipaddr, iface.netmask, iface.gateway, '\r\n'.join(nameservers))
    print """<input type="Submit" name="submit" value="Update IP Configuration"></form></body></html>"""

print """
  </body>
</html>"""
