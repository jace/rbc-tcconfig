#!/usr/bin/env python

"""
Script to set or disable GRUB's password. Has to be called as root.
"""

import sys
import os

def updateGrub(menufile, password, md5pass = False):
    if password:
        if md5pass:
            passwdline = 'password --md5 %s\n' % password
        else:
            passwdline = 'password %s\n' % password
    else:
        passwdline = '' # No password
    lines = open(menufile, 'r').readlines()
    linefound = False
    insertpos = None
    for counter in range(len(lines)):
        line = lines[counter]
        if line.strip().replace('\t', ' ').startswith('password '):
            if not linefound:
                linefound = True
                lines[counter] = passwdline
            else:
                lines[counter] = '# ' + line # Disable all but first find
        elif line.strip().replace('\t', ' ').startswith('## password'):
            insertpos = counter
    if not lines[-1].endswith('\n') and lines[-1] != '':
        lines[-1] += '\n'
    if not linefound:
        if insertpos is not None:
            lines.insert(insertpos+1, passwdline)
        else:
            lines.append(passwdline)

    # Save and exit. Take backup first.
    # Will fail on Windows if file already exists, but our target is Linux.
    os.rename(menufile, menufile+'~')
    open(menufile, 'w').writelines(lines)

def main(argv):
    if len(argv) != 3:
        print >> sys.stderr, """Usage: %s grub-menu-file password

The grub menu file on Debian-based systems is usually /boot/grub/menu.lst.
To disable the password, use "-". Passwords may currently only be in
plain text.""" % argv[0]
        return 1
    menufile, password = argv[1:]
    if password == '-':
        password = None
    return updateGrub(menufile, password)

if __name__=='__main__':
    sys.exit(main(sys.argv))
