#!/bin/bash
#
# rbc_set_access_profile.sh: script to enable user specific acl(s) in the
# scquid.conf and inform the running Squid about it.
#
# rbc_set_access_profile.sh looks for the line of the form `##include profile'
# in the `squid.conf.template' file and replaces it with the actual user
# profile. While the template file is located under the squid config directory;
# The user profile file must be located under `profiles' directory under the
# squid config directory[default: /etc/squid].
#
# Run this script with the same user privileges as that of the Squid process.
#

VERSION="0.4"
PATH="/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin:$PATH"

# to suppress the getopts error messages
OPTERR=0
OPTIND=0

SIGHUP=1
SQDPID=`lsof -i 4:3128 -Fp | cut -dp -f2`

# Default Squid configuration parameters.
confd="/etc/squid";
cachd="/var/spool/squid";
squsr="proxy";
sqcmd="/etc/init.d/squid start";

usage ()
{
    printf "Usage: %s [OPTIONS] <user-name>\n" "$0";
}


printh ()
{
    fmt="%-18s %s\n";

    usage;
    printf "\n %s\n" "Options:";
    printf "$fmt" "   -c <dir-name>" \
                  "specify squid cache directory [default: $cachd]";
    printf "$fmt" "   -d <dir-name>" \
                  "specify squid config directory [default: $confd]";
    printf "$fmt" "   -h" "display this help";
    printf "$fmt" "   -p <pid>" "spcify squid process-id";
    printf "$fmt" "   -u <user-name>" \
                  "specify squid cache directory owner name";
    printf "$fmt" "   -v" "display version information";
    printf "\n%s\n" "Report bugs to <prasad.pandit@comat.com>";
}


check_options ()
{
    while getopts ":c:d:hp:u:v" c $*
    do
        case $c in
            :)
            printf "$0: argument missing for \`-%s'\n" $OPTARG;
            exit 1;
            ;;

            c)
            if [ ! -d $OPTARG ]; then
                printf "$0: could not access directory: \`%s'\n" $OPTARG;
                exit 1;
            fi
            cachd="$OPTARG";
            ;;

            d)
            if [ ! -d $OPTARG ]; then
                printf "$0: could not access directory: \`%s'\n" $OPTARG;
                exit 1;
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
                exit 1;
            fi
            SQDPID=$OPTARG;
            ;;

            u)
            squsr=`id -u $OPTARG`;
            if [ -z $squsr ]; then
                printf "$0: invalid user: \`%s'\n" $OPTARG;
                exit 1;
            fi
            squsr="$OPTARG";
            ;;

            v)
            printf "%s version %s\n" "$0" "$VERSION";
            exit 0;
            ;;

            *)
            printf "$0: invalid option: \`-%s'; Try \`$0 -h'\n" $OPTARG;
            exit 1;
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
        exit 1;
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
        exit 1;
    fi
    if [ -z "$SQDPID" ]; then
        printf "$0: seems like Squid is not listening on port 3128\n";
        chown -R $squsr:$squsr $cachd;
#
#       $sqcmd -f $conff;
        $sqcmd;
        sleep 1s;
#
#       SQDPID=`cat /var/run/squid.pid 2> /dev/null`;
        SQDPID=`lsof -i 4:3128 -Fp | cut -dp -f2`;
        if [ -z "$SQDPID" ]; then
            printf "$0: could not start squid; Aborting!\n";
            exit 1;
        fi
    fi
    printf "$0: using Squid(pid: %d) config: \`%s'\n" $SQDPID "$conff";
    printf "$0: including acls from \`%s'\n" $proff;

    # do the actual include operation
    tmpcfg="/tmp/cfg.squid";
    sed -e "s:^##include.*profile:cat < $proff:e" $conft > $tmpcfg;

    #
    # Check if the new config file is okay or not; And if okay, then copy it
    # to the actual Squid config file.
    squid -f $tmpcfg -k parse
    if [ $? -ne 0 ]; then
        printf "$0: erroneous profile file \`%s'\n" $proff;
        rm -f $tmpcfg;
        exit 1;
    fi
    cat $tmpcfg > $conff;
    rm -f $tmpcfg;

    # Tell Squid to re-read the configuration file.
    squid -f $conff -k reconfigure

    exit 0;
}
