#!/usr/bin/env python

"""
Config installer. Takes a backup of existing configuration and restores
from it when the overriding package is uninstalled. Ensures backup is
not lost when the overriding package is reinstalled.

:Author: Kiran Jonnalagadda
:Version: 0.1
:Copyright: Copyright (C) 2007, Comat Technologies Pvt Ltd
"""

__docformat__ = 'restructuredtext'
__revision__ = '$Id$'

import sys
import os
from optparse import OptionParser

class BackupError(Exception):
    pass

def backupName(path):
    """
    Returns a backup file name that is in the same containing folder as
    the source name. ::

        >>> temp = os.tempnam('/tmp')
        >>> backup = backupName(temp)
        >>> temp != backup
        True
        >>> os.path.dirname(temp) == os.path.dirname(backup)
        True
    """
    return "%s.orig" % path

def restoreConfig(installpath):
    """
    Restores the original config file to the given path. Returns True on
    successful restore, False if no backup was found. Raises an
    exception if the config path exists but is not a regular file. ::

        >>> temp = os.tempnam('/tmp')
        >>> restoreConfig(temp)
        False
        >>> open(backupName(temp), 'wb').write('')
        >>> restoreConfig(temp)
        True
        >>> os.path.exists(backupName(temp))
        False
        >>> os.path.exists(temp)
        True
        >>> os.remove(temp)
        >>> os.mkdir(temp)
        >>> open(backupName(temp), 'wb').write('')
        >>> try:
        ...   restoreConfig(temp)
        ... except BackupError:
        ...   print "caught"
        ...
        caught
        >>> os.remove(backupName(temp))
        >>> os.rmdir(temp)
    """
    backupname = "%s.orig" % installpath
    if not os.path.isfile(backupname):
        return False
    elif os.path.isfile(installpath):
        os.remove(installpath) # Required on Windows, where rename will fail
    elif os.path.exists(installpath) and not os.path.isfile(installpath):
        raise BackupError, "Config path exists but is not a regular file."
    os.rename(backupname, installpath)
    return True

def backupConfig(installpath, forcebackup=False):
    """
    Conditionally backs up a config file, checking first that it hasn't
    already been backed up. Returns True on successful backup, False if
    backup already exists or config file does not.

    If forcebackup is specified, will overwrite any existing backup. ::

        >>> temp = os.tempnam('/tmp')
        >>> backupConfig(temp)
        False
        >>> backupConfig(temp, forcebackup=True)
        False
        >>> open(temp, 'wb').write('')
        >>> backupConfig(temp)
        True
        >>> os.path.exists(backupName(temp))
        True
        >>> os.path.exists(temp)
        False
        >>> open(temp, 'wb').write('')
        >>> backupConfig(temp)
        False
        >>> backupConfig(temp, True)
        True
        >>> os.remove(backupName(temp))
        >>> os.mkdir(backupName(temp))
        >>> open(temp, 'wb').write('')
        >>> try:
        ...   backupConfig(temp)
        ... except BackupError:
        ...   print "caught"
        ...
        caught
        >>> try:
        ...   backupConfig(temp, forcebackup=True)
        ... except BackupError:
        ...   print "caught"
        ...
        caught
        >>> os.rmdir(backupName(temp))
        >>> os.remove(temp)
    """
    backupname = "%s.orig" % installpath
    if not os.path.isfile(installpath):
        return False
    elif os.path.isfile(backupname) and not forcebackup:
        return False
    elif os.path.isfile(backupname) and forcebackup:
        os.remove(backupname) # Required on Windows, where rename will fail
    elif os.path.exists(backupname) and not os.path.isfile(backupname):
        raise BackupError, "Backup path exists and is not a file."
    os.rename(installpath, backupname)
    return True

def getUidGid(user, group):
    """
    Returns uid and gid given user and group names. Makes the best
    effort it can:

    - If user or group is not specified, the current process values are
      used.
    - If specified, the Unix databases are looked up.
    - If not found there either, the values are assumed to be integer
      ids.

    If all options to obtain uid or gid fail, a ValueError exception is
    raised.

    This function only works on POSIX-compliant systems. ::

        >>> uid, gid = getUidGid(None, None)
        >>> isinstance(uid, int)
        True
        >>> isinstance(gid, int)
        True
        >>> uid == os.getuid()
        True
        >>> gid == os.getgid()
        True

        Test for 'root' user. We can't test for root group because Mac OS X
        calls it 'wheel'. Our tests must pass on Mac OS X and Linux.

        >>> getUidGid('root', None)[0]
        0

        >>> getUidGid(os.getuid(),os.getgid()) == (os.getuid(),os.getgid())
        True
        >>> getUidGid(str(os.getuid()), None) == (os.getuid(), os.getgid())
        True
        >>> getUidGid(None, str(os.getgid())) == (os.getuid(), os.getgid())
        True
        >>> try:
        ...   getUidGid('la-la-lingoleela', None) # Random unlikely id
        ... except ValueError:
        ...   print "caught"
        ...
        caught
    """
    if user is None:
        uid = os.getuid()
    elif isinstance(user, basestring):
        import pwd
        try:
            uid = pwd.getpwnam(user).pw_uid
        except KeyError:
            try:
                uid = int(user)
            except ValueError:
                raise ValueError, "Invalid user %s." % user
    elif isinstance(user, int):
        uid = user
    else:
        raise ValueError, "Invalid user %s." % user

    if group is None:
        gid = os.getgid()
    elif isinstance(group, basestring):
        import grp
        try:
            gid = grp.getgrnam(group).gr_gid
        except KeyError:
            try:
                gid = int(group)
            except ValueError:
                raise ValueError, "Invalid group %s." % group
    elif isinstance(group, int):
        gid = group
    else:
        raise ValueError, "Invalid group %s." % group
    return uid, gid

def installConfig(installpath, newconfig, options):
    """
    Backs up existing config file and installs new config at specified
    path. ::

        >>> class dummy:
        ...   pass
        ...
        >>> options = dummy()
        >>> options.force = False
        >>> options.quiet = True
        >>> options.mode = '0644'

        We can't test for whether the user/group options are workable
        unless this test is running as root, which may or may not be the
        case (most likely not). Since the test has to be consistent,
        we'll skip this, for now.

        >>> options.user = None
        >>> options.group = None

        >>> testold = os.tempnam('/tmp')
        >>> open(testold, 'w').write('test-backup-old')
        >>> testnew = os.tempnam('/tmp')
        >>> open(testnew, 'w').write('test-backup-new')
        >>> installConfig(testold, testnew, options)
        >>> open(testold, 'r').read() == 'test-backup-new'
        True
        >>> oct(os.stat(testold).st_mode)[-4:]
        '0644'
        >>> open(backupName(testold), 'r').read() == 'test-backup-old'
        True
        >>> testagain = os.tempnam('/tmp')
        >>> open(testagain, 'w').write('test-backup-again')
        >>> options.mode = '0600'
        >>> installConfig(testold, testagain, options)
        >>> oct(os.stat(testold).st_mode)[-4:]
        '0600'
        >>> open(testold, 'r').read() == 'test-backup-again'
        True
        >>> open(backupName(testold), 'r').read() == 'test-backup-old'
        True
        >>> options.force = True
        >>> installConfig(testold, testagain, options)
        >>> open(backupName(testold), 'r').read() == 'test-backup-again'
        True

        Tests done. Clean up.

        >>> os.remove(backupName(testold))
        >>> os.remove(testold)
        >>> os.remove(testnew)
        >>> os.remove(testagain)
    """
    # TODO: Test user/group if test is running as root.
    status = backupConfig(installpath, options.force)
    if status is False and not options.quiet:
        print "Avoiding overwriting existing backup of %s" % installpath
    # Read data before attempting to write to new location, to ensure we
    # don't create a blank file in the event of the input file being
    # unreadable.
    data = open(newconfig, 'rb').read()
    open(installpath, 'wb').write(data)
    os.chmod(installpath, int(options.mode, 8))
    if options.user is not None or options.group is not None:
        uid, gid = getUidGid(options.user, options.group)
        os.chown(installpath, uid, gid)

def main(argv):
    """
    Backs up and restores configuration files.
    """
    parser = OptionParser(
        usage="%prog [options] install-path new-config-file")
    parser.add_option('-r', '--restore', action="store_true",
        default=False, help="Restore original config file.")
    parser.add_option('-m', '--mode', default='0644',
        help="File permissions [default 0644]")
    parser.add_option('-u', '--user', default=None,
        help="File owner [default is calling user]")
    parser.add_option('-g', '--group', default=None,
        help="File group [default is calling user's primary group]")
    parser.add_option('-q', '--quiet', action="store_true",
        default=False, help="Quiet operation (except error messages)")
    parser.add_option('-f', '--force', action="store_true",
        default=False, help="Overwrite existing backup, if any")
    parser.add_option('-t', '--test', action="store_true",
        default=False, help="Run internal tests, ignoring options and args")
    (options, args) = parser.parse_args(argv[1:])

    if options.test:
        import doctest
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning,
            message="tempnam is a potential security risk to your program",
            module=__name__)
        doctest.testmod()
        return 0

    if not ((options.restore is True and len(args) == 1) or len(args) == 2):
        print >> sys.stderr, "Error: install path and config file must be specified. Use the -h option for details."
        return 1
    installpath = args[0]
    if not options.restore:
        newconfig = args[1]
    else:
        newconfig = None
    if options.restore:
        restoreConfig(installpath)
        return 0
    else:
        installConfig(installpath, newconfig, options)
        return 0

if __name__=='__main__':
    sys.exit(main(sys.argv))
