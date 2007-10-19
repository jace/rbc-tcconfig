#!/bin/bash

if [ "r$1" -eq "r" ]; then
    echo "Usage: $0 /path/to/vmware/image/"
    exit 1
fi

cp -av $1 /home/vmplayer/windows

if [ `ls -1 /home/vmplayer/windows/*.vmx | wc -l` -ne 1 ]; then 
    echo "There is more than one vmx file present. Please move the appropriate file to winxp.vmx"
else
    mv /home/vmplayer/windows/*.vmx /home/vmplayer/windows/winxp.vmx
fi

chown -R vmplayer:vmplayer /home/vmplayer/windows
chmod -R go-rwx /home/vmplayer/windows
