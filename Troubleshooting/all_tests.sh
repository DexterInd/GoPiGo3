#! /bin/bash

cd /home/pi/Dexter/GoPiGo3/Troubleshooting/

echo "==============================="
echo "GoPiGo3 Troubleshooting Script"
echo "==============================="

echo "GoPiGo3 Troubleshooting Script log" > log.txt
sudo bash hardware_and_firmware_test.sh 2>&1| tee -a log.txt

echo ""
cp log.txt /home/pi/Desktop/log.txt
echo "Log has been saved to Desktop. Please copy it and send it by email or upload it on the forums"
