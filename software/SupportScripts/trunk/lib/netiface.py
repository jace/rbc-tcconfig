#!/usr/bin/env python

"""
Module to read (and write?) settings from Debian's /etc/network/interfaces file.
"""

from StringIO import StringIO

class NetworkInterface:
    """
    Class to hold network interface details.
    """
    
    def __init__(self, ifname, ifpresent=False, ifauto=True, iftype='dhcp', ipaddr=None,
                 netmask=None, gateway=None):
        self.ifname =  ifname
        self.ifpresent = ifpresent
        self.ifauto = ifauto # Indicates auto start, not auto address (DHCP). See ifstatic.
        self.iftype = iftype
        self.ipaddr = ipaddr
        self.netmask = netmask
        self.gateway = gateway

    def render(self):
        if not self.ifpresent:
            return '' # Blank if interface was not present
        result = StringIO()
        if self.ifauto:
            print >> result, "auto %s" % self.ifname
        print >> result, "iface %s inet %s" % (self.ifname, self.iftype)
        if self.iftype == 'static':
            print >> result, "\taddress %s" % self.ipaddr
            print >> result, "\tnetmask %s" % self.netmask
            if self.gateway is not None:
                print >> result, "\tgateway %s" % self.gateway
        return result.getvalue()

def readNameServers(resolvfile="/etc/resolv.conf"):
    """
    Returns nameservers listed in provided resolv file. Does not handle other directives.
    """
    if hasattr(resolvfile, 'read'):
        lines = resolvfile.readlines()
    else:
        lines = file(resolvfile, 'rt').readlines()
    nameservers = []
    for line in lines:
        line = line.strip().replace('\t', ' ')
        if line.startswith('nameserver'):
            tokens = line.split(' ')
            while '' in tokens:
                tokens.remove('')
            nameservers.append(tokens[1])
    return nameservers

def readInterface(interfacesfile, ifname):
    """
    Returns details of specified interface.
    """
    if hasattr(interfacesfile, 'read'):
        lines = interfacesfile.readlines()
    else:
        lines = file(interfacesfile, 'rt').readlines()
    # pass
    iface = NetworkInterface(ifname, ifpresent=False, ifauto=False)

    ifaceparsing = False # Determines parser status

    for line in lines:
        if not ifaceparsing:
            if line.strip() == "auto %s" % ifname:
                # Interface is already auto. No need to add another auto line.
                iface.ifauto = True
            if line.strip().startswith("iface %s inet" % ifname):
                iface.ifpresent = True
                ifaceparsing = True
                iftype =  line.strip().split(" ")[-1]
                iface.iftype = iftype
                if iftype != 'static':
                    break
                else:
                    iface.ifstatic = True # Assume it is "static"
        else:
            sline = line.strip()
            sline = sline.replace("\t", " ") # Convert tabs into spaces.
            tokens = sline.split(" ")
            while "" in tokens:
                tokens.remove("")
            # Still parsing iface. Check if values are valid or not.
            if sline.startswith("gateway"):
                iface.gateway = tokens[1]
            elif sline.startswith("address"):
                iface.ipaddr = tokens[1]
            elif sline.startswith("netmask"):
                iface.netmask = tokens[1]
            elif sline.startswith("#"):
                # Comment. Ignore.
                pass
            else:
                # We got something else. End of interface definition.
                ifaceparsing = False
    return iface

if __name__=='__main__':
    for ifname in ['lo', 'eth0', 'eth0:0', 'eth1']:
        print readInterface("/etc/network/interfaces", ifname).render()
