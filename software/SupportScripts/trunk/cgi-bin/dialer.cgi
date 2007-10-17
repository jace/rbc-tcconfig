#!/usr/bin/env python
import cgi
import os

print "Content-type: text/html\n"


html = """<HTML><HEAD><TITLE>Internet Dialer</TITLE></HEAD>
<BODY>
<form method="POST" action="dialer.cgi">
<input name="dial" id="dial" type="hidden" value="%s">
<input  type="SUBMIT" value="%s">
</BODY>
</HTML>"""

form = cgi.FieldStorage()
dial = 0
done = None
try:
  dial = form['dial'].value
except KeyError:
  dial = 0


if dial == "1":
  done = (0, 'Disconnect')
  print html % done
  os.system("cgidialer &")
elif dial == "0":
  os.system('cgidialer stop')
  done = (1, 'Connect')
  print html % done
else:
  done = (1, 'Connect Now')
  print html % done
#except:
#  done = (1, 'Connect Now')

