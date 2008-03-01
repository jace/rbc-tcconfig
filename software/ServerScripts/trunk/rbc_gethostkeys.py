#!/usr/bin/env python
"""
Script to check a mail account, retrieve mail containing host keys,
create a local user account for the host and install the keys for SSH
key-based access to the account.
"""

import os
import sys
import getpass
import poplib, email
import mimetypes
import warnings
from optparse import OptionParser

try: # Since readline may not be available.
    import readline
except ImportError:
    pass


class EmailFiles:
    """
    Class to process mail attachments and hold them as binary objects.
    """
    def __init__(self, msgbody):
        message = email.message_from_string(msgbody)
        self.Subject = message.get('Subject', '')
        self.From = message.get('From', '')
        self.To = message.get('To', '')
        self.Cc = message.get('Cc', '')
        self.Date = message.get('Date', '')
        self.message = message

        # Don't do these until parse() is called. Speeds up filtering.
        self.files = {}

    def parse(self):
        """
        Parse message's attachments. Named attachments go into the 'files'
        dictionary and all others are dicarded.
        """
        for part in self.message.walk():
            if part.get_content_maintype() == 'multipart':
                continue # ??
            filename = os.path.basename(part.get_filename() or '')
            if filename:
                self.files[filename] = part.get_payload(decode=True)

class SSHKeyParser:
    """
    Class to process SSH keys received via email. Requires an EmailFiles object
    as parameter.
    """
    def __init__(self, efiles):
        self.efiles = efiles
        self.hostid = efiles.Subject.split(' ')[2]
        unpackdir = os.tempnam('/tmp', 'rbcssh')
        os.mkdir(unpackdir)
        for filename, filebody in self.efiles.files.items():
            fp = open(os.path.join(unpackdir, filename), 'wb')
            fp.write(filebody)
            fp.close()
        self.dir = unpackdir

    def deploy(self):
        """Deploy SSH keys"""
        return os.system('rbc_hostadd "%s" "%s"' % (self.hostid, self.dir))

    def close(self):
        """Clean up"""
        for keyfile in self.efiles.files:
            os.remove(os.path.join(self.dir, keyfile))
        os.rmdir(self.dir)

    __del__ = close


def promptyesno(prompt, default=None):
    """
    Prompt the user with yes/no question. Returns True or False. The default
    answer may be one of Yes (True), No (False) or None.
    """
    if default not in [True, False, None]:
        raise ValueError, "Invalid default answer %s." % default

    if default is None:
        prompt = prompt + ' (y/n):'
    elif default:
        prompt = prompt + ' (Y/n):'
    else:
        prompt = prompt + ' (y/N):'

    answer = None
    while answer is None:
        answer = raw_input(prompt)
        if not answer:
            answer = default
        elif answer[0] in ['t', 'T', '1', 1, 'y', 'Y']:
            answer = True
        elif answer[0] in ['f', 'F', '0', 0, 'n', 'N']:
            answer = False
        else:
            answer = None
    return answer

def run(host, username, password, dryrun=False, auto=False):
    """
    Polls mail server for new mail and parses received host keys.
    If testrun is true, messages are not deleted from the server and no local
    machine accounts are created.
    """
    # Login to POP3 server
    pop = poplib.POP3(host)
    pop.user(username)
    pop.pass_(password)
    # Check for mail
    message_count = len(pop.list()[1])
    print "Processing %d message(s)..." % message_count
    for i in range(1, message_count+1):
        print "Message %d of %d..." % (i, message_count)
        msg_body = '\r\n'.join(pop.retr(i)[1])
        fileob = EmailFiles(msg_body)
        if fileob.Subject.startswith('SSH '):
            print fileob.Subject
            fileob.parse()
            print "Files:", repr(fileob.files.keys())
            keys = SSHKeyParser(fileob)
            # TODO: Prompt user here on what to do with message.
            if auto:
                deploy = True
            else:
                deploy = promptyesno("Deploy keys for host id %s?" % keys.hostid,
                                     True)
            if deploy:
                if dryrun:
                    print "Dry run, skipping deployment."
                else:
                    status = keys.deploy()
                    if status != 0:
                        print "Deployment failed, leaving message on server."
                    else:
                        # TODO, FIXME: Never ever delete without saving!
                        # Let's just put this stuff in a temp folder somewhere
                        pop.dele(i)
        else:
            # Message looks like junk.
            if not auto:
                delete = promptyesno("Message looks like junk. Delete?", True)
                if dryrun:
                    print "Dry run, ignoring input and leaving message on server."
                else:
                    if delete:
                        pop.dele(i)
            else:
                # Automatic mode. Delete if not dry run.
                if dryrun:
                    print "Dry run, leaving junk message on server."
                else:
                    pop.dele(i)
    # Clean up
    pop.quit()
    print "All done!"

def main(argv):
    "%prog options"

    warnings.filterwarnings("ignore", category=RuntimeWarning,
        message="tempnam is a potential security risk to your program",
        module=__name__)

    parser = OptionParser(usage=main.__doc__)
    parser.add_option('-H', '--host', type="string", default="",
                      help="Mail server hostname")
    parser.add_option('-U', '--username', type="string", default="",
                     help="Mail server login username")
    parser.add_option('-p', '--password', type="string", default="",
                      help="Mail server login password (prompted if blank)")
    parser.add_option('-a', '--auto', action="store_true", default=False,
                       help="Automatic mode, no user prompts")
    parser.add_option('-d', '--dryrun', action="store_true", default=False,
                      help="Dry run, do not delete messages or create accounts")
    (options, args) = parser.parse_args(argv[1:])

    if options.host != '' and options.username != '':
        if options.password == '':
            options.password = getpass.getpass()
    else:
        print >> sys.stderr, "Usage: %s options. Use -h for details" % argv[0]
        return 1
    run(host=options.host, username=options.username, password=options.password,
        dryrun=options.dryrun, auto=options.auto)


if __name__=='__main__':
    sys.exit(main(sys.argv))
