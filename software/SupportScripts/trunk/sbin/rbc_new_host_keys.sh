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

rm -f ~tcconfig/.ssh/id_rsa ~tcconfig/.ssh/id_rsa.pub
rm -f ~tcconfig/.ssh/id_dsa ~tcconfig/.ssh/id_dsa.pub

# Create host id
# XXX: The -r parameter to sed only works in GNU sed. BSD sed requires -E.
# We don't bother with the difference since we're only targetting Linux.
echo -n "Determining host id... "
echo $(/sbin/ifconfig -a | grep -E '(ether|HWaddr|lladdr)' | sed -re 's/.*(ether|lladdr|HWaddr)( |\t)*([0-9a-fA-F:-]+).*/\3/; s/://g' | head -n1)-$(cat /etc/hostname | sed -e 's/-//g') > /etc/hostid
chmod 644 /etc/hostid
cat /etc/hostid


# Regenerate keys
echo "Making new host keys..."
/var/lib/dpkg/info/openssh-server.postinst configure 2> /dev/null

mkdir ~tcconfig/.ssh 2> /dev/null
chown tcconfig:tcconfig ~tcconfig/.ssh
chmod 700 ~tcconfig/.ssh

su - tcconfig -c "cd ~/.ssh; ssh-keygen -q -f id_rsa -t rsa -N ''; ssh-keygen -q -f id_dsa -t dsa -N ''"

# Set a flag so this script isn't called again
touch /etc/ssh/.rbchostkey

MAILDOMAIN="rbc.comat.com"
if [ -f /etc/default/maildomain ]; then
    . /etc/default/maildomain
fi
