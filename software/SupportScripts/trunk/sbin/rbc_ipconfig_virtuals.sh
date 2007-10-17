#!/bin/sh

IFACES="`sed -n -e 's/[ \t]*iface \(eth.:.\) inet.*/\1/p' /etc/network/interfaces`"

for IFACE in $IFACES; do
    ifdown "$IFACE"
    ifup "$IFACE"
done
