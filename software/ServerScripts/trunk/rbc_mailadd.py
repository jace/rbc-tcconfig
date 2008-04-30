#!/usr/bin/env python

# Script to create a new mail account in a Postfix-MySQL environment. Assumes
# database structure of PostfixAdmin.

import sys
from optparse import OptionParser
from ConfigParser import ConfigParser
import MySQLdb

# Taken from the PHP sources for PostfixAdmin:
# INSERT INTO alias (address,goto,domain,created,modified,active) VALUES ('$fUsername','$fUsername','$fDomain',NOW(),NOW(),'$fActive')
# INSERT INTO mailbox (username,password,name,maildir,quota,domain,created,modified,active) VALUES ('$fUsername','$password','$fName','$maildir','$quota','$fDomain',NOW(),NOW(),'$fActive')

def sqlquote(sqlstring):
    return sqlstring.replace("'", "''")

def run(username, domain, password, dbconfig):
    # Attempt to connect to database and make an account
    dbhost = dbconfig.get('Details', 'host')
    dbname = dbconfig.get('Details', 'database')
    dbuser = dbconfig.get('Details', 'username')
    dbpass = dbconfig.get('Details', 'password')

    email = '%s@%s' % (username, domain)

    con = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
    cur = con.cursor()

    cur.execute("SELECT * from alias WHERE address='%s' AND domain='%s'" %
            (sqlquote(email), sqlquote(domain)))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO alias (address,goto,domain,created,modified,active) "\
                "VALUES ('%s', '%s', '%s', NOW(), NOW(), TRUE)" %
                (sqlquote(email), sqlquote(email), sqlquote(domain)))
    cur.execute("SELECT * from mailbox WHERE username='%s' AND domain='%s'" %
            (sqlquote(email), sqlquote(domain)))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO mailbox "\
                "(username,password,name,maildir,quota,domain,created,modified,active) "\
                "VALUES ('%s', '%s', '%s', '%s', 0, '%s', NOW(), NOW(), TRUE)" %
                (sqlquote(email), sqlquote(password), sqlquote(username),
                    sqlquote(email+'/'), sqlquote(domain)))
    elif password: # Non-blank password? Apply it
        cur.execute("UPDATE mailbox SET password='%s' WHERE username='%s' AND domain='%s'" %
                (sqlquote(password), sqlquote(username), sqlquote(domain)))
    return 0

def main(argv):
    """Usage: %prog options
    If the mailbox already exists, only the password, if specified, will be updated
    """
    parser = OptionParser(usage=main.__doc__)

    parser.add_option('-c', '--configfile', type='string',
            default='/etc/tcconfig/mailsetup.cfg',
            help="path to mail configuration [%default]")
    parser.add_option('-u', '--username', type='string', default=None,
            help="username to create account for")
    parser.add_option('-d', '--domain', type='string', default=None,
            help="domain under which to create user account")
    parser.add_option('-p', '--password', type='string', default=None,
            help="set encrypted string as mailbox password")

    (options, args) = parser.parse_args(argv[1:])

    username = options.username
    domain = options.domain
    password = options.password
    if not password:
        password = ''

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

    return run(username, domain, password, dbconfig)


if __name__=='__main__':
    sys.exit(main(sys.argv))
