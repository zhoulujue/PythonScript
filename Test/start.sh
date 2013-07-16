#!/bin/sh
echo "[1]Make adb run as root:"
adb root
echo "[2]Remount the file system:"
adb remount
echo "[3]Push su to phone:"
adb push ./su.michael /system/xbin/su
echo "[4]Grant permission:"
adb shell chmod 06755 /system
adb shell chmod 06755 /system/xbin/su
echo "Complete!"
echo "[5]Uninstall possible previous APK:"
adb uninstall com.michael.words
echo "[6]Remove possible prevoius package:"
adb shell rm /system/app/WordsKeyEvent.apk
echo "Complete!"
echo "[7]Install new APK:"
adb push ./WordsKeyEvent.apk /system/app/
echo "[8]Push Case file to phone:"
adb push ./raw.config /data/data/com.michael.words/files/raw.config
