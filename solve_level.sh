#!/usr/bin/sh

echo "Taking screenshot"
adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png /tmp/screen.png

echo "Getting board solution"
python3 screen2board.py > /tmp/cmds.sh
cat /tmp/cmds.sh

echo "Executing solution"
sh /tmp/cmds.sh

# Tap "next" button.
adb shell input tap 475 380
sleep 1

