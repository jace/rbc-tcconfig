#!/usr/bin/env python

# Script to patch /etc/network/interfaces to add ethX:Y as a static/dhcp network.
# Script must be run as root.

# The proper way to write this script is with a token parser and lexical
# analyser, but we're lazy, so we'll do a simple series of string
# comparisons. It works for the most part.

__version__='0.2'
__revision__='$Id$'

import sys
#import re # TODO: use re instead of string comparisons.
from optparse import OptionParser

parser = OptionParser(usage="%prog [options] interface-name",
                      version="%%prog %s" % __version__)
parser.add_option('-f', '--file', type="string", default="/etc/network/interfaces",
                  help="Interfaces file [default /etc/network/interfaces]")
parser.add_option('-t', '--type', type="string", default="dhcp",
                  help="Type of configuration: dhcp or static [default dhcp]")
parser.add_option('-i', '--ipaddr', type="string", default=None,
                  help="IP Address [default None]")
parser.add_option('-n', '--netmask', type="string", default="255.255.255.0",
                  help="Netmask [default 255.255.255.0]")
parser.add_option('-g', '--gateway', type="string", default=None,
                  help="Gateway [default None]")
parser.add_option('-r', '--remove', action="store_true", default=False,
                  help="Remove interface, ignoring all other options")

(iface, interfaces) = parser.parse_args(sys.argv[1:])
if len(interfaces) < 1:
    print >> sys.stderr, "Error: Interface must be specified. Use -h for help."
    sys.exit(-1)
elif len(interfaces) > 1:
    print >> sys.stderr, "Error: Only one interface may be specified."
    sys.exit(-1)
ifname = interfaces[0]

if iface.type == "static" and iface.ipaddr is None:
    print >> sys.stderr, "IP Address must be specified for static IP settings."
    sys.exit(-2)

# Open file, remove existing interfaces, add new as auto starting interface

lines = file(iface.file, 'rt').readlines()

autoiface = False
autoifaceline = -1
ifacepresent = False
ifacevalid = True
ifacelinestart = -1
ifacelineend = -1

ifaceparsing = False # Determines parser status

for counter in range(len(lines)):
    line = lines[counter]
    if not ifaceparsing:
        if line.strip() == "auto %s" % ifname:
            # Interface is already auto. No need to add another auto line.
            autoiface = True
            autoifaceline = counter
        if line.strip().startswith("iface %s inet" % ifname):
            ifacepresent = True
            ifaceparsing = True
            ifacelinestart = counter
            if line.strip() != "iface %s inet %s" % (ifname, iface.type):
                ifacevalid = False
    else:
        sline = line.strip()
        # Still parsing iface. Check if values are valid or not.
        if sline.startswith("gateway"):
            if iface.gateway is None:
                ifacevalid = False
            elif sline != "gateway %s" % iface.gateway:
                ifacevalid = False
        elif sline.startswith("address"):
            if sline != "address %s" % iface.ipaddr:
                ifacevalid = False
        elif sline.startswith("netmask"):
            if sline != "address %s" % iface.netmask:
                ifacevalid = False
        elif sline.startswith("#") or sline == '':
            # Comment or blank line. Ignore.
            pass
        else:
            # We got something else. End of interface definition.
            ifaceparsing = False
            ifacelineend = counter

if ifaceparsing:
    ifaceparsing = False
    ifacelineend = len(lines) - 1 # Interface found at end of file.

if ifacelineend == ifacelinestart:
    ifacelineend += 1 # XXX: Crude hack. Not sure why this is needed.

# Now replace iface if needed.

if iface.remove:
    if autoiface:
        lines.pop(autoifaceline)
        if autoifaceline <= ifacelinestart:
            ifacelinestart -= 1
            ifacelineend -= 1
    if ifacepresent:
        lines = lines[:ifacelinestart] + lines[ifacelineend:]
else:
    newlines = []

    if not autoiface:
        newlines.append("auto %s\n" % ifname)

    if not ifacevalid or not ifacepresent:
        # Insert new lines now
        newlines.append("iface %s inet %s\n" % (ifname, iface.type))
        if iface.type == 'static':
            newlines.append("\taddress %s\n" % iface.ipaddr)
            newlines.append("\tnetmask %s\n" % iface.netmask)
            if iface.gateway is not None:
                newlines.append("\tgateway %s\n" % iface.gateway)

    if ifacepresent and not ifacevalid:
        # Remove lines from file
        newlines.append('\n') # Insert blank line at end.
        lines = lines[:ifacelinestart] + newlines + lines[ifacelineend:]
    else:
        lines.extend(newlines)

outfile = file(iface.file, 'w')
outfile.writelines(lines)
