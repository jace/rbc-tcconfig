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

VERSION="0.1"
prog=`basename $0`;

usage ()
{
    echo "Usage: $prog [OPTIONS] [/path/to/folder] ..."
    echo -e "       $prog [OPTIONS] [file-1.list file-2.list ...]\n"
    echo "List files and folders can be specified in the same invocation."
}


printh ()
{
    fmt="%-17s %s\n";

    usage;
    printf "\n%s\n" " Options:"
    printf "$fmt"   "   -h, --help" "display this help"
    printf "$fmt"   "   -v, --version" "display version information"
    printf "\n%s\n" "Report bugs to <prasad.pandit@comat.com>"
}

makelist ()
{
    DIRNAME=`dirname "$1"`
    LISTFILE=`basename "$1"`
    PRODUCT=${LISTFILE%%.list}

    if [ "$PRODUCT" = "sources" ]; then
        return
    fi

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
        echo "Rebuilding $PRODUCT..."
        find . -name Makefile -execdir make -f '{}' \;
        sudo epm -f deb "$PRODUCT"
    fi

    cd $OLDPWD
}


#
# main ()
{
    arg=$@
    if [ -z "$arg" ]; then
        arg="$PWD"
    fi
    if [ "$1" = "-h" -o "$1" = "--help" ]; then
        printh
        exit 1
    elif [ "$1" = "-v" -o "$1" = "--version" ]; then
        echo "$prog - $VERSION"
        exit 1
    elif [ `expr "$1" : "^[-]\+.*"` -gt 0 ]; then
        echo "$prog: invalid option: \`$1'"
        exit -1
    fi
    
    echo `date +%D-%T` "$prog $arg"
    for LIST in $arg; do
        if [ `expr "$LIST" : "^[-]\+.*"` -gt 0 ]; then
            echo "$prog: file name must not start with a \`-': $LIST"
            continue
        fi
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
