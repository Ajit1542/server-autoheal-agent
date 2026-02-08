#!/bin/bash

LOGFILE="/var/log/syslog"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -f "$LOGFILE" ]; then
    echo "Compressing old messages log..."
    cp $LOGFILE ${LOGFILE}_$TIMESTAMP
    gzip ${LOGFILE}_$TIMESTAMP

    echo "Truncating original messages log..."
    : > $LOGFILE
fi
