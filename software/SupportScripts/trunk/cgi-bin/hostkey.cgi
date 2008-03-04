#!/usr/bin/env python

import cgi
import os
import sys
import subprocess

def keyGenAllowed():
    """Returns True if this machine needs host key regeneration."""
    if os.path.exists("/etc/ssh/.rbchostkey"):
        return False
    else:
        return True

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
    # Confirm that the flag is not set and re-generate host keys.
    print """<h1>Regenerating host keys...</h1>"""
    print "<pre>"
    sys.stdout.flush()
    process = subprocess.Popen(["sudo", "/usr/sbin/rbc_new_host_keys"], env=os.environ,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        for line in process.stdout.readlines():
            print cgi.escape(line)
        for line in process.stderr.readlines():
            print cgi.escape(line)
        sys.stdout.flush()
    print "</pre>"
if form.has_key('remail'):
    # Confirm that remailing the host keys.
    print  """<h1>Remailing the host kets...</h1>"""
    print "<pre>"
    sys.stdout.flush()
    process = subprocess.Popen(["sudo", "/usr/bin/rbc_new_host_keys"], env=os.environ,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        for line in process.stdout.readlines():
            print cgi.escape(line)
        for line in process.stderr.readlines():
            print cgi.escape(line)
        sys.stdout.flush()
    print "<pre>"
else:
    # Display submit button
    print '<form action="" method="post">'
    if keyGenAllowed():
        print '<input type="submit" name="submit" value="Regenerate Host Keys" />'
    else:
        print "<p>This computer's host keys have already been generated. Just remail them.</p>"
	print '<input type="submit" name="remail" value="Mail again the Host Keys" />'
    print '</form>'

print """</body></html>"""
