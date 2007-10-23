#!/usr/bin/env python

"""
Script to reconfigure IP interfaces, DNS and hostname. Has to be called as root.
"""

import os
import sys
from optparse import OptionParser

domainname = "rbc.comat.com"

# FIXME: Use domainname from /etc/maildomain if present.

def updateHosts(hostsfile, hostname, domainname, hostnamefile):
    """
    This function will update hosts file ::
    
       >>> tempname = os.tempnam('/tmp')
       >>> tempname1 = os.tempnam('/tmp')
       >>> updateHosts(tempname,'testhost', domainname, tempname1)
       >>> lines = open(tempname,'r').readlines()
       >>> linepresent = 0
       >>> for line in lines:
       ...     if line == '127.0.1.1 testhost.%s testhost\\n' % domainname:
       ...         linepresent += 1
       ...
       >>> linepresent
       1
       >>> open(tempname1,'r').read()
       'testhost\\n'

       >>> os.remove(tempname)
       >>> os.remove(tempname1)
    """
    # FIXME: Do a test with a file containing some real data.
    hostsline = '127.0.1.1 %s.%s %s\n' % (hostname, domainname, hostname)
    if not os.path.exists(hostsfile):
        lines = []
    else:
        lines = file(hostsfile, 'r').readlines()
    linefound = False
    for counter in range(len(lines)):
        line = lines[counter]
        if line.strip().startswith('127.0.1.1'):
            linefound = True
            lines[counter] = hostsline
    if not linefound:
        lines.append(hostsline)
    file(hostsfile, 'w').writelines(lines)
    file(hostnamefile, 'w').write('%s\n' % hostname)

def updatePostfix(filename):
    """
    To update postfix main.cf file ::
    
        >>> tempname = os.tempnam('/tmp')
        >>> tfile = open(tempname,'w')
        >>> tfile.write('myhostname\\n')
        >>> tfile.write('myhost\\n')
        >>> tfile.write('myhostname\\n')
        >>> tfile.close()
        >>> updatePostfix(tempname)
        >>> lines = open(tempname,'r').readlines()
        >>> linepresent = 0
        >>> for line in lines:
        ...     if line.startswith('#myhostname'):
        ...         linepresent += 1
        ...     if line.startswith('myhostname'):
        ...         linepresent -= 1
        ...
        >>> linepresent
        2
        >>> os.remove(tempname)
    """
    lines = file(filename, 'r').readlines()
    for counter in range(len(lines)):
        line = lines[counter]
        if line.strip().startswith('myhostname'):
            lines[counter] = '#'+line
    file(filename, 'w').writelines(lines)

def updateResolvConf(nameservers, filename):
    """
    This function will update the dns information:
    
        >>> tempname = os.tempnam('/tmp')
        >>> updateResolvConf(['192.168.1.13','192.168.42.13'], tempname)
        >>> lines = open(tempname,'r').readlines()
        >>> linepresent = 0
        >>> if lines[0] == 'nameserver 192.168.1.13\\n':
        ...     linepresent += 1
        ...
        >>> if lines[1] == 'nameserver 192.168.42.13\\n':
        ...     linepresent += 1
        ...
        >>> linepresent
        2
    """
    if len(nameservers) > 0:
        resolv = file(filename, 'wt')
        for ns in nameservers:
            print >> resolv, "nameserver %s" % ns
        resolv.close()


def oldmain(itype, ipaddr, netmask, gateway, hostname, *nameservers):
    # Step 1: Update IP config. Use rbc_iface_patch for this.
    ifpatch_command = "/usr/sbin/rbc_iface_patch.py -t '%s' -i '%s' -n '%s' -g '%s' eth0" % (
              itype, ipaddr, netmask, gateway)
    os.system(ifpatch_command)
    # Step 2: Update resolv.conf if itype is not 'dhcp'
    if itype != 'dhcp' and len(nameservers) > 0:
        resolv = file('/etc/resolv.conf', 'wt')
        for ns in nameservers:
            print >> resolv, "nameserver %s" % ns
        resolv.close()
    # Step 3: Update hostname in /etc/hostname and /etc/hosts
    file('/etc/hostname', 'wt').write('%s\n' % hostname)
    updateHosts('/etc/hosts', hostname, domainname)
    updatePostfix('/etc/postfix/main.cf')
    os.system("hostname '%s'" % hostname)
    # Step 4: Restart networking
    os.system('/etc/init.d/networking restart > /dev/null')
    os.system('/usr/sbin/rbc_ipconfig_virtuals &> /dev/null')
    os.system('/etc/init.d/postfix restart > /dev/null')

def updateInterfaces(iftype, address, netmask, gateway, interfaces):
        parameters = ['/usr/sbin/rbc_iface_patch']
        parameters.extend(['-f', interfaces])
        parameters.extend(['-t', iftype])
        if address is not None:
            parameters.extend(['-i', address])
        if netmask is not None:
            parameters.extend(['-n', netmask])
        if gateway is not None:
            parameters.extend(['-g', gateway])
        parameters.append('eth0')
    	os.spawnv(os.P_WAIT, '/usr/sbin/rbc_iface_patch' , parameters)

def main(argv):
    # FIXME: We need tests here. Does it actually update only one file if asked to, or does it mess around the place?
    parser = OptionParser(
        usage="%prog [options]")
    parser.add_option('--hostname',
        default=None, help="The hostname of the system")
    parser.add_option('--hostsfile', default='/etc/hosts',
        help="hosts file path [default is /etc/hosts]")
    parser.add_option('-a', '--address', default=None,
        help="IP address of the system [default is None]")
    parser.add_option('-n', '--netmask', default=None,
        help="Netmask of the network")
    parser.add_option('-i', '--iftype',
        default=None, help="Network type (dhcp / static) [default is None]")
    parser.add_option('-g', '--gateway', default=None, help="Network Gateway")
    
    parser.add_option('--resolvconf', default='/etc/resolv.conf', help="Resolve conf file [default is /etc/resolve]")
    
    parser.add_option('-d', '--dns', type="string", action="append", dest="nameservers", 
        default=None, help="DNS nameserver address (may be multiple) ")
    parser.add_option('-q', '--quiet',
        default=None, help="Do not display texts")
    parser.add_option('--interfaces',
        default='/etc/network/interfaces', help="The interfaces filename [default is /etc/network/interfaces]")
    parser.add_option('--postfixcf',
        default='/etc/popstfix/main.cf', help="The postfix configuration file [default is /etc/postfix/main.cf]")
    parser.add_option('-p', '--postfix', action="store_true",
        default=False, help=" update postfix hostname config (Default: False)")
    parser.add_option('-r', '--restart', action="store_true",
        default=False, help=" Restart affected services (networking, postfix) [default is False]")
    parser.add_option('-t', '--test', action="store_true",
        default=False, help="Run internal tests, ignoring options and args")
    
    parser.add_option('--hostnamefile', default='/etc/hostname', help="Hostname file [default is /etc/hostname]")
    parser.add_option('--initnetwork', default='/etc/init.d/networking', help="init file for network [default is /etc/init.d/networking]")
    parser.add_option('--initpostfix', default='/etc/init.d/postfix', help="init file for postfix [default is /etc/init.d/postfix]")
    
    (options, args) = parser.parse_args(argv[1:])

    if options.test:
        import doctest
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning,
            message="tempnam is a potential security risk to your program",
            module=__name__)
        doctest.testmod()
        return 0

    if options.iftype is not None:
        updateInterfaces( options.iftype, options.address, options.netmask, options.gateway, options.interfaces)

    if options.nameservers is not None:
        updateResolvConf(options.nameservers, options.resolvconf)

    if options.hostsfile is not None:
        updateHosts(options.hostsfile, options.hostname, domainname, options.hostnamefile)
        if options.postfix:
            updatePostfix(options.postfixcf)

    if options.restart:
        os.system(options.initnetwork + ' restart > /dev/null 2>&1')
        os.system(options.initpostfix + ' restart > /dev/null 2>&1')


if __name__=='__main__':
    sys.exit(main(sys.argv))
