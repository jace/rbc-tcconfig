#!/usr/bin/env python

import cgi
import os
import sys
import subprocess

print "Content-Type: text/html"
print # End of headers
print """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>Host Key Configuration</title>
    <link rel="stylesheet" type="text/css" href="/styles.css" />
  </head>
  <body>
"""

form = cgi.FieldStorage()
if form.has_key('submit'):
    print """<h1>Regenerating hostpassword...</h1>"""
    print "<pre>"
    sys.stdout.flush()
    process = subprocess.Popen(["sudo", "/etc/cron.weekly/hostpassword"], env=os.environ,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        for line in process.stdout.readlines():
            print cgi.escape(line)
        for line in process.stderr.readlines():
            print cgi.escape(line)
        sys.stdout.flush()
    print "</pre>"
    print "<p>Done.</p>"
else:
    # Display submit button
    print "<p>After your host keys have been submitted and validated on the server, your computer needs to retrieve a password for itself. This is required for the computer to authorise user logins with the server.</p>"
    print "<p>Password retrieval is done automatically once a week, but you may also ask for it to be retrieved again now.</p>"
    print '<form action="" method="post">'
    print '<input type="submit" name="submit" value="Retrieve New Host Password" />'
    print '</form>'

print """</body></html>"""
