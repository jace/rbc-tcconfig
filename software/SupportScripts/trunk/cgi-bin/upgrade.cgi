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
    <title>Printer Configuration</title>
    <link rel="stylesheet" type="text/css" href="/styles.css" />
  </head>
  <body>
"""

form = cgi.FieldStorage()
if form.has_key('submit'):
    # Do apt upgrade now and display results.
    print """<h2>Updating list of available software</h2>"""
    print "<pre>"
    sys.stdout.flush()
    process = subprocess.Popen(["sudo", "apt-get", "-y", "update"], env=os.environ,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        for line in process.stdout.readlines():
            print cgi.escape(line)
        for line in process.stderr.readlines():
            print cgi.escape(line)
        sys.stdout.flush()
    print "</pre>"
    print """<h2>Downloading and installing updates</h2>"""
    print "<pre>"
    sys.stdout.flush()
    process = subprocess.Popen(["sudo", "apt-get", "-y",
            "--allow-unauthenticated", "dist-upgrade"],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    while process.poll() is None:
        for line in process.stdout.readlines():
            print cgi.escape(line)
        for line in process.stderr.readlines():
            print cgi.escape(line)
        sys.stdout.flush()
    print "</pre>"
else:
    # Display submit button
    print """<form action="" method="post">
        <input type="submit" name="submit" value="Upgrade Software" />
        </form>"""

print """</body></html>"""
