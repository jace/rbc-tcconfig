#!/bin/sh

# Remove old host keys
cd /etc/ssh
echo Removing existing host keys.
rm -f ssh_host_key     ssh_host_key.pub
rm -f ssh_host_rsa_key ssh_host_rsa_key.pub
rm -f ssh_host_dsa_key ssh_host_dsa_key.pub

# Regenerate keys
/var/lib/dpkg/info/openssh-server.postinst configure
