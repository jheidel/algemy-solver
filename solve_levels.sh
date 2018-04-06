#!/bin/sh

set -e

while true; do 
        echo "Taking screenshot"
        SCREENSHOT=/tmp/screen.png
        adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png $SCREENSHOT

        echo "Getting board solution"
        SOLUTION=/tmp/adb_cmds.sh
        python3 screen2board.py -x $SCREENSHOT | tee $SOLUTION

        echo "Executing solution"
        sh $SOLUTION

        # Tap "next" button.
        adb shell input tap 475 380
        sleep 1
done
