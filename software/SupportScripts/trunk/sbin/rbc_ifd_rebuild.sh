#!/bin/bash

interfaces="$1"
ifd="$2"

usage () {
    echo "Usage: $0 /etc/network/interfaces /etc/network/interfaces.d"
    exit 1
    }

if [ -z "$interfaces" ]; then
    usage
fi

if [ -z "$ifd" ]; then
    usage
fi

if [ ! -d "$ifd" ]; then
    echo "Interface definition folder could not be found"
    usage
fi

# ------------------------------------------------------------

# Empty the interfaces file without replacing it.
# No good reason why we do this instead of deleting the file
# and creating it afresh. The potential advantage use cases --
# of the file being hard linked elsewhere or of us not being
# root and the containing folder having a o+s bit set -- don't
# really apply to us.
#
# So perhaps we're doing this only because it's a cool hack.
cat > "$interfaces" << EOF
EOF

# Append all available files into interface file. Ignore files
# that may be backup files using bash's GLOBIGNORE facility.

GLOBIGNORE="$ifd/*~:$ifd/*.*"

for iface in "$ifd"/*; do
    cat "$iface" >> "$interfaces"
    echo >> "$interfaces"
done
