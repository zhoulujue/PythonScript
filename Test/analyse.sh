#!/bin/sh
echo "[1]Make adb run as root:"
adb root
echo "[2]Remount the file system:"
adb remount
echo "[3]Get result file from phone:"
adb pull /data/data/com.michael.words/files/raw.config
adb pull /data/data/com.michael.words/files/result.txt
echo "[4]Start analysing:"
python ./AnalyseResultLocal.py
