#!/usr/bin/env python
import os
import cgi
import re
import csv

printers_list_file = "/etc/cups/printers-list.csv"
cups_printers_conf_template = "/etc/cups/printers.conf.template"
printer_reconfigure_command = "/usr/sbin/rbc_printers_reconfigure"
printer_conf_cgi = "printer.cgi" # This file

class PrinterInfo:
    def __init__(self, name, searchstring, substitutestring):
        self.name = name
        self.search_str = re.compile(searchstring)
        self.subst_str = substitutestring
        self.devices = []

print "Content-Type: text/html"
print # End of headers
print """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>Printer Configuration</title>
    <link rel="stylesheet" type="text/css" href="/styles.css" />
"""

print "<!-- Reading printer list -->"
reader = csv.reader(file(printers_list_file, 'r'))
printerlist = []

for row in reader:
    printer = PrinterInfo(row[0], row[1], row[2])
    printerlist.append(printer)

print "<!-- Done -->"

form = cgi.FieldStorage()
if form.has_key('submit'):
    print """
  </head>
  <body>
"""
    templatevalues = {}
    for printer in printerlist:
        templatevalues[printer.subst_str] = form.getvalue(printer.subst_str, '')
    templatefile = file(cups_printers_conf_template, 'r').read() % templatevalues
    print "<h1>Saving new printer configuration...</h1>"
    print """<pre>%s</pre>""" % cgi.escape(templatefile)
    prin, prout = os.popen2(printer_reconfigure_command)
    prin.write(templatefile)
    prin.close()
    print "</body></html>"
elif form.has_key('refresh'):
    print """
  </head>
  <body>
"""
    print '<form action="" method="post">'
  
    lst = os.popen('lpinfo -v').readlines()
    for line in lst:
        for printer in printerlist:
            if printer.search_str.search(line) != None:
                printer.devices.append(line)
   
    for printer in printerlist:
        print "<h2>%s</h2>" % printer.name
        print """<table><tr><th align="left">Select</th><th align="left">Device</th></tr>"""
        firstdevice = True
        for i in printer.devices:
            values = i.split(' ')
            print """<tr><td><input type="radio" name="%s" value="%s" %s></td><td>%s</td>""" % (printer.subst_str, values[1][:-1], (firstdevice and 'checked="checked" /' or ' /'), values[1][:-1])
            firstdevice = False
        print "</table>"
    print """<input type="Submit" name="submit" value="Configure Printers"></form></body></html>"""  
else:
    print """
    <meta http-equiv="Refresh" content="0; url=%s?refresh=1" />
  </head>
  <body>
    <p>Please wait, searching for available printers...</p>
"""  % printer_conf_cgi
print """
  </body>
</html>"""
