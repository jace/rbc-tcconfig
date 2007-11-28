#!/bin/sh

# Check that we're not being called after keys have already been generated.
if [ -f /etc/ssh/.rbchostkey ]; then
    echo "Host key regeneration not required."
    exit 1
fi

# Remove old host keys
cd /etc/ssh
echo "Removing existing host keys..."
rm -f ssh_host_key     ssh_host_key.pub
rm -f ssh_host_rsa_key ssh_host_rsa_key.pub
rm -f ssh_host_dsa_key ssh_host_dsa_key.pub

rm -f ~manager/.ssh/id_rsa ~manager/.ssh/id_rsa.pub
rm -f ~manager/.ssh/id_dsa ~manager/.ssh/id_dsa.pub

# Regenerate keys
echo "Making new host keys..."
/var/lib/dpkg/info/openssh-server.postinst configure 2> /dev/null

mkdir ~manager/.ssh 2> /dev/null
chown manager:manager ~manager/.ssh
chmod 700 ~manager/.ssh

su - manager -c "cd ~/.ssh; ssh-keygen -q -f id_rsa -t rsa -N ''; ssh-keygen -q -f id_dsa -t dsa -N ''"

# Set a flag so this script isn't called again
touch /etc/ssh/.rbchostkey

MAILDOMAIN="rbc.comat.com"
if [ -f /etc/default/maildomain ]; then
    . /etc/default/maildomain
fi

echo "Mailing public keys..."
filemailer -s "SSH Host: $(cat /etc/hostname)" -n -a /etc/ssh/ssh_host_dsa_key.pub -a /etc/ssh/ssh_host_rsa_key.pub hostkey@"$MAILDOMAIN"
filemailer -s "SSH manager: $(cat /etc/hostname)" -n -a ~manager/.ssh/id_rsa.pub -a ~manager/.ssh/id_dsa.pub hostkey@"$MAILDOMAIN"
