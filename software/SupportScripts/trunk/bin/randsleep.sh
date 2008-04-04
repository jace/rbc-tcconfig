#!/bin/bash

limit=`expr "$1" + 0 2> /dev/null`

if [ -z "$limit" ]; then
    echo "Usage: randsleep seconds"
    echo "randsleep will sleep for a random period not exceeding specified seconds."
    exit 1
fi

randsec=$RANDOM
while [ $randsec -lt $limit ]; do
    randsec=$(($randsec + $RANDOM))
done

randsec=$(($randsec % $limit))
sleep ${randsec}s
exit 0
