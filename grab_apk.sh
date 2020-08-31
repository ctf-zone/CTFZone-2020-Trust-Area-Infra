#!/bin/bash

# set -o xtrace

MAX_LENGTH=10485760

TEAM_ID=$1
TEAM_BACK=$2


URL="http://$TEAM_BACK/apk/app.apk"

LENGTH=$(wget -T 1 -t 1 --spider "$URL" 2>&1 | awk '/Length/ {print $2}')

# echo "LENGTH: $LENGTH"

if [[ -z "$LENGTH" ]]; then
    exit 42
fi

# NOP if bigger then limit
if [[ $LENGTH -gt $MAX_LENGTH ]]; then
    exit 73
fi

TMP_FILE=$(mktemp)
DST="/home/ctfzone/Desktop/APKs/Team$TEAM_ID.apk"

GRAB_RESULT=$(timeout 5 wget -T 5 -t 1 -q -o /dev/null "$URL" -O $TMP_FILE && echo "OK" || echo "FUCK")

# echo "GRABBED: $GRAB_RESULT"

if [[ $GRAB_RESULT == "FUCK" ]]; then
    exit 101
fi

CHECK_PKG_RESULT=$(aapt dump badging $TMP_FILE | grep -o "package: name='ctfz.trustarea.client.team$TEAM_ID'")

# echo "PKG: $CHECK_PKG_RESULT"

if [[ -z $CHECK_PKG_RESULT ]]; then
    echo "TEAM#$TEAM_ID FAILED"
    exit 404
fi

# echo "REPLACE: $TMP_FILE -> $DST"
mv $TMP_FILE $DST


