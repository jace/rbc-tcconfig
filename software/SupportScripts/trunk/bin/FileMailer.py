#!/usr/bin/env python

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
import pwd
import socket
import time
import sys
from optparse import OptionParser
from smtplib import *
import bz2

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class FileMailer:
    """Main class for mails"""

    def __init__(self,recipients , subject="", text=""):
        self.smtpserver = None
        self.recipients = recipients
        self.subject = subject
        self.text = text
        self.msg = MIMEMultipart()
        self.msg['From'] = self.__getFrom()
        self.msg['To'] = ", ".join(recipients)
        self.msg['Date'] = formatdate(localtime=True)
        self.msg['Subject'] = subject
        self.msg.attach( MIMEText(text) )

    def __getFrom(self):
        return pwd.getpwuid(os.geteuid())[0] + '@' + socket.getfqdn()

    def send(self, server, port):
        self.smtpserver = SMTP(server, port)
        self.smtpserver.sendmail(self.__getFrom(), self.recipients, self.msg.as_string() )
        self.smtpserver.close()

    def attach(self, filename, filedata):
        """Function to send the mails
        """
        #for filetobesend in filestobesend:
        part = MIMEBase('application', "octet-stream")
        if not hasattr(filedata, 'read'):
            filedata = file(filedata, 'rb').read()
        else:
            filedata = filedata.read()
        part.set_payload(filedata)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))
        self.msg.attach(part)

    def attachtext(self, filename, text):
        zipped = StringIO()
        zipped.write(bz2.compress(text))
        zipped.seek(0)
        self.attach(filename + '.bz2', zipped)

def main(argv):
    "%prog [options] recipients..."
    parser = OptionParser(usage=main.__doc__)
    parser.add_option('-s', '--subject', type="string", default="",
                      help="Subject of the message [default BLANK]")
    parser.add_option('-n', '--nobody', action="store_true", default=False,
                      help="Do not read body text from stdin [default is to read]")
    parser.add_option('-z', '--zip', action="store_true", default=False,
                      help="Compress text from standard input [default False]")
    parser.add_option('-a', '--attachment', type="string", action="append", dest="files",
                      help="Attach file")
    parser.add_option('-r', '--relayhost', type="string", default="localhost",
                      help="Mail relay host [default localhost]")
    parser.add_option('-p', '--port', type="int", default=25,
                      help="Mail server port [default 25]")
    (options, recipients) = parser.parse_args(argv[1:])

    if len(recipients) < 1:
        print >> sys.stderr, "At least one recipient must be specified."
        return -1

    # Do something here
    default_text = "FileMailer with arguments: %s\r\n" % " ".join([repr(arg) for arg in argv])
    if not options.nobody:
        user_text = sys.stdin.read()
    else:
        user_text = ""
    if options.zip or user_text == "":
        body_text = default_text
    else:
        body_text = user_text

    filemailer = FileMailer(recipients, options.subject, body_text)
    if options.zip and user_text != '':
        filemailer.attachtext("stdin.txt", user_text)
    if options.files != None:
        for attachment in options.files:
            filemailer.attach(attachment, attachment)
    filemailer.send(options.relayhost, options.port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
