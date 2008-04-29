#!/usr/bin/env python

# Script to create a new mail account in a Postfix-MySQL environment. Assumes
# database structure of PostfixAdmin.

import os
import sys
from optparse import OptionParser
from ConfigParser import ConfigParser
import MySQLdb

# INSERT INTO alias (address,goto,domain,created,modified,active) VALUES ('$fUsername','$fUsername','$fDomain',NOW(),NOW(),'$fActive')
# INSERT INTO mailbox (username,password,name,maildir,quota,domain,created,modified,active) VALUES ('$fUsername','$password','$fName','$maildir','$quota','$fDomain',NOW(),NOW(),'$fActive')

def sqlquote(sqlstring):
    return sqlstring.replace("'", "''")

def run(username, domain, dbconfig):
    # Attempt to connect to database and make an account
    dbhost = dbconfig.get('Details', 'host')
    dbname = dbconfig.get('Details', 'database')
    dbuser = dbconfig.get('Details', 'username')
    dbpass = dbconfig.get('Details', 'password')
    maildirpath = dbconfig.get('Details', 'maildirpath')

    con = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
    cur = con.cursor()

    cur.execute("INSERT INTO alias (address,goto,domain,created,modified,active) VALUES ('%s', '%s', '%s', NOW(), NOW(), TRUE)" % (sqlquote(username), sqlquote(username), sqlquote(domain)))
    cur.execute("INSERT INTO mailbox (username,password,name,maildir,quota,domain,created,modified,active) VALUES ('%s', '', '%s', '%s', 0, '%s', NOW(), NOW(), TRUE)" % (sqlquote(username), sqlquote(username), sqlquote(os.path.join(maildirpath, domain, username), sqlquote(domain))))

def main(argv):
    parser = OptionParser(usage=main.__doc__)

    parser.add_option('-c', '--configfile', type='string',
            default='/etc/tcconfig/mailsetup.cfg',
            help="Path to mail configuration [%default]")
    parser.add_option('-u', '--username', type='string', default=None,
            help="Username to create account for")
    parser.add_option('-D', '--domain', type='string', default=None,
            help="Domain under which to create user account")

    (options, args) = parser.parse_args(argv[1:])

    username = options.username
    domain = options.domain

    if not username:
        print >> sys.stderr, "Username not specified. Use -h for help."
        return 1

    if not domain:
        if username.find('@') != -1:
            try:
                username, domain = username.split('@')
            except UnpackError:
                print >> sys.stderr, "Invalid username or domain: %s" % options.username
                return 3
        else:
            print >> sys.stderr, "Domain not specified. Use -h for help."
            return 2

    dbconfig = ConfigParser()
    try:
        dbconfig.readfp(open(options.configfile))
    except IOError:
        print >> sys.stderr, "Could not read config file: %s" % options.configfile
        return 4

    run(username, domain, dbconfig)


if __name__=='__main__':
    sys.exit(main(sys.argv))
