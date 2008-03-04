#!/bin/sh

MAILDOMAIN="rbc.comat.com"
if [ -f /etc/default/maildomain ]; then
    . /etc/default/maildomain
fi

echo "Mailing public keys..."
filemailer -s "SSH Host: $(cat /etc/hostid)" -n -a /etc/ssh/ssh_host_dsa_key.pub -a /etc/ssh/ssh_host_rsa_key.pub hostkey@"$MAILDOMAIN"
filemailer -s "SSH tcconfig: $(cat /etc/hostid)" -n -a ~tcconfig/.ssh/id_rsa.pub -a ~tcconfig/.ssh/id_dsa.pub hostkey@"$MAILDOMAIN"
