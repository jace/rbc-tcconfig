#!/bin/bash
#
# rbc_access_profile.sh: script to enable user specific acl(s) in the
# scquid.conf and inform the running squid about it.
#
# Run this script with the same user privileges as that of the Squid process.
#

VERSION="0.2"
PATH="/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin:$PATH"

# to suppress the getopts error messages
OPTERR=0
OPTIND=0

SIGHUP=1
SQDPID=`lsof -i 4:3128 -Fp | cut -dp -f2`

# Default Squid configuration directory.
confd="/etc/squid"

usage ()
{
    printf "Usage: %s [OPTIONS] <user-name>\n" "$0";
}


printh ()
{
    fmt="%-20s %s\n";

    usage;
    printf "\n %s\n" "Options:";
    printf "$fmt" "   -d <dir-name>" "specify squid config directory";
    printf "$fmt" "   -h" "display this help";
    printf "$fmt" "   -p <pid>" "spcify squid process-id";
    printf "$fmt" "   -v" "display version information";
    printf "\n%s\n" "Report bugs to <prasad.pandit@comat.com>";
}


check_options ()
{
    while getopts ":d:hp:v" c $*
    do
        case $c in
            :)
            printf "$0: argument missing for \`-%s'\n" $OPTARG;
            exit 0;
            ;;

            d)
            if [ ! -d $OPTARG ]; then
                printf "$0: could not access directory: \`%s'\n" $OPTARG;
                exit 0;
            fi
            confd="$OPTARG";
            ;;

            h)
            printh;
            exit 0;
            ;;

            p)
            if [ `expr $OPTARG : "[0-9]\+"` -ne `expr length $OPTARG` ]; then
                printf "$0: <pid> must be numeric: \`%s'\n" $OPTARG;
                exit 0;
            fi
            SQDPID=$OPTARG;
            ;;

            v)
            printf "%s version %s\n" "$0" "$VERSION";
            exit 0;
            ;;

            *)
            printf "$0: invalid option: \`-%s'; Try \`$0 -h'\n" $OPTARG;
            exit 0;
        esac
    done

    return $(($OPTIND - 1));
}

# main ()
{
    check_options $*;
    shift $?;
    if [ $# -lt 1 ]; then
        printf "$0: <user-name> missing!\n";
        usage;
        exit 0;
    fi

    conff="$confd/squid.conf"
    proff="$confd/profiles/$1.conf"
    conft="$confd/squid.conf.template"
    if [ ! -r $proff ]; then
        printf "$0: could not access file \`%s'\n" $proff;
        proff="$confd/profiles/fallback.conf";
    fi
    if [ ! -r $conft ]; then
        printf "$0: could not access file \`%s'\n" $conft;
        exit 0;
    fi
    if [ -z "$SQDPID" ]; then
        printf "$0: seems like Squid is not listening on port 3128\n";
        exit 0;
    fi
    printf "$0: using Squid(pid: %d) config: \`%s'\n" $SQDPID "$conff";
    printf "$0: including acls from \`%s'\n" $proff;

    # do the actual include operation
    sed -e "s:^#include.*profile:cat < $proff:e" $conft > $conff;

    # Tell Squid to re-read the configuration file.
    printf "$0: signaling Squid \`$SQDPID'\n";
    kill -$SIGHUP $SQDPID;

    exit 0;
}
