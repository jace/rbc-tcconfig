#!/bin/sh

# Script to share the 'user' user's ~/.Xauthority file with another user
# Can be dangerous in a true multi-user system -- do not reuse elsewhere.

rm -f /home/"$1"/.Xauthority
cp /home/user/.Xauthority /home/"$1"/.Xauthority
chown "$1":"$1" /home/"$1"/.Xauthority
