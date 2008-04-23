#!/bin/bash

# Script to re-create deb files if the corresponding EPM list files have
# been updated. Works in two ways:
#
#  1. If list files have been specified, processes them
#  2. If a folder has been specified, looks for list files within

if [ "$#" -eq 0 ]; then
    echo "Usage: makedeb.sh /path/to/folder ..."
    echo "       makedeb.sh file1.list file2.list ..."
    echo
    echo "List files and folders can be specified in the same invocation."
    exit 1
fi

makelist () {
    DIRNAME="`dirname \"$1\"`"
    LISTFILE="`basename \"$1\"`"
    PRODUCT="${LISTFILE%%.list}"
    VERSION=$(grep %version "$LISTFILE" | head -1 | sed -e "s/$(echo -e '\t')/ /g" | cut -f2 -d\ )
    RELEASE=$(grep %release "$LISTFILE" | head -1 | sed -e "s/$(echo -e '\t')/ /g" | cut -f2 -d\ )

    if [ "$RELEASE" != "" ] && [ "$RELEASE" -ne 0 ]; then
        VERSION="$VERSION-$RELEASE"
    fi

    cd "$DIRNAME"
    DEBFILE="`find . -type f -name \"$PRODUCT-$VERSION*.deb\" -newer \"$LISTFILE\"`"
    if [[ "$LISTFILE" -nt "$DEBFILE" ]]; then
        echo Rebuilding $PRODUCT...
        find -name Makefile -execdir make -f '{}' \;
        # Decide on whether to package for specific architecture or for all
        # Look for binary files
        find -type f -execdir file '{}' \; | grep -E ':[ \t]*(ELF|Mach-O).*executable.*(386|x86-64)' > /dev/null
        if [ $? -eq 0 ] ; then
            # Found Package for architecture
            sudo epm -f deb "$PRODUCT"
        else
            # Package for noarch (in Debian: "all")
            sudo epm -f deb -a all "$PRODUCT"
        fi
    fi
}

for LIST in "$@"; do
    if [ -d "$LIST" ]; then
        for LIST2 in "$LIST"/*.list; do
            makelist "$LIST2"
        done
    else
        makelist "$LIST"
    fi
done
