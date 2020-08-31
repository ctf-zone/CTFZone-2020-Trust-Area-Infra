#!/bin/bash


# set -o xtrace

TEAM_ID=$1
ISO_TIME=$2

APK_PATH="/home/ctfzone/Desktop/APKs/Team$TEAM_ID.apk"

TEAM_APKS="/home/ctfzone/Desktop/TeamAPKs/Team$TEAM_ID"
STORAGE_PATH="$TEAM_APKS/storage"
INSTALL_LOG_PATH="$TEAM_APKS/install.log"


# Copy to storage
APK_MD5=$(md5sum $APK_PATH | awk '{print $1}')
APK_STORAGE_PATH="$STORAGE_PATH/$APK_MD5.apk"
if [[ ! -f "$APK_STORAGE_PATH" ]]; 
then
    cp "$APK_PATH" "$APK_STORAGE_PATH"
fi


# Make ISO-time record
echo "[$ISO_TIME] - $APK_STORAGE_PATH" >> "$INSTALL_LOG_PATH"

