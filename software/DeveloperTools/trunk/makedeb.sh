#!/bin/bash
#
# Script to re-create deb files if the corresponding EPM list files have
# been updated. Works in two ways:
#
# 1. If list files have been specified, processes them
# 2. If a folder has been specified, looks for list files within
#
# Make sure all paths are *absolute* paths, beginning with slash (`/').
#

prog=`basename $0`;

usage ()
{
    echo "Usage: $prog [/path/to/folder] ..."
    echo -e "       $prog [file-1.list file-2.list ...]\n"
    echo "List files and folders can be specified in the same invocation."
}


makelist ()
{
    DIRNAME=`dirname "$1"`
    LISTFILE=`basename "$1"`
    PRODUCT=${LISTFILE%%.list}

    cd $DIRNAME

    VERSION=$(grep %version "$LISTFILE" | head -1 \
                            | sed -e "s/$(echo -e '\t')/ /g" | cut -f2 -d\ )
    RELEASE=$(grep %release "$LISTFILE" | head -1 \
                            | sed -e "s/$(echo -e '\t')/ /g" | cut -f2 -d\ )

    if [ "$RELEASE" != "" ] && [ "$RELEASE" -ne 0 ]; then
        VERSION="$VERSION-$RELEASE"
    fi

    DEBFILE=`find . -type f -name "$PRODUCT-$VERSION"*.deb`
    if [ "$LISTFILE" -nt "$DEBFILE" ]; then
        echo "Rebuilding [00;33m$PRODUCT[00m..."
        find . -name Makefile -execdir make -f '{}' \;
        sudo epm -f deb "$PRODUCT"
    fi

    cd $OLDPWD
}


#
# main ()
{
    arg="$@"
    if [ -z "$arg" ]; then
        arg="$PWD"
    fi
    if [ "$1" = '-h' -o "$1" = '--help' ]; then
        usage
        exit 1
    fi
    
    echo `date +%D-%T` "$prog $arg"
    for LIST in "$arg"; do
        if [ -d "$LIST" ]; then
            #
            # This will build entire sub-tree under $LIST. Of course if that is
            # required, ie. If `.list' file is newer than `.deb' file.
            #
            for LIST2 in `find $LIST -name \*.list`; do
                makelist "$LIST2"
            done
        else
            makelist "$LIST"
        fi
    done
}
