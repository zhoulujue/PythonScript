adb root
adb remount
adb push ./su.michael /system/xbin/su
adb shell chmod 06755 /system
adb shell chmod 06755 /system/xbin/su
adb uninstall com.michael.words
adb shell rm /system/app/WordsKeyEvent.apk
adb push WordsKeyEvent.apk /system/app/
adb push raw.config /data/data/com.michael.words/files/raw.config


