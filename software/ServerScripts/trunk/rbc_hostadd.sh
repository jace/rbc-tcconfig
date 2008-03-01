#!/bin/sh

# Script to create a new user account for a given host id and to
# setup SSH key-based access to the account. Can also be used to
# deploy new keys to an existing account.

if [ $# -lt 1 ]; then
	echo Usage: $0 hostid [hostkey1] [hostkey2] ...
	echo
	echo Hostkeys are copied to the new account\'s .ssh folder. The
	echo originals are left untouched. Must be called as root.
	exit 19 # Not using 1,2 etc since we return useradd status below
fi

if [ "$UID" -ne 0 ]; then
	echo $0: Must be called as root user.
	exit 20
fi

HOSTID="$1"
HOMEDIR="/home/$HOSTID"
shift

echo -n "Creating machine account... "
useradd --comment "$HOSTID" --home "$HOMEDIR" --create-home "$HOSTID"
STAT="$?"
case "$STAT" in
	0)
		echo "done."
		;;
	9)
		echo "skipped, already exists."
		;;
	*)
		echo "failed, exit code $STAT. See useradd(8) for details."
		exit "$STAT"
		;;
esac

mkdir "$HOMEDIR/.ssh"
chmod 700 "$HOMEDIR/.ssh"
chown "$HOSTID":"$HOSTID" "$HOMEDIR/.ssh"
for FILE in "$@"; do
	BASEFILE=`basename "$FILE"`
	cp -f "$FILE" "$HOMEDIR/.ssh/$BASEFILE"
	chmod 600 "$HOMEDIR/.ssh/$BASEFILE"
	chown "$HOSTID":"$HOSTID" "$HOMEDIR/.ssh/$BASEFILE"
done
cat "$HOMEDIR/.ssh/id_rsa.pub" "$HOMEDIR/.ssh/id_dsa.pub" > "$HOMEDIR/.ssh/authorized_keys" 2> /dev/null
chmod 600 "$HOMEDIR/.ssh/authorized_keys"
chown "$HOSTID":"$HOSTID" "$HOMEDIR/.ssh/authorized_keys"
exit 0
