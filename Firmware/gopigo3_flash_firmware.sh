#! /bin/bash

# Reads the path of the GoPiGo3 repository
REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\GoPiGo3)")
# Gets the absolute path of the latest Firmware update 
FW_UPDATE_FILE=$(sudo find "$REPO_PATH"/Firmware/ -name *.bin)
echo "Updating the GoPiGo3 Firmware with '$FW_UPDATE_FILE'."
sudo openocd -f interface/raspberrypi2-native.cfg -c "transport select swd; set CHIPNAME at91samc20j18; source [find target/at91samdXX.cfg]; adapter_khz 250; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program $FW_UPDATE_FILE verify; reset" -c "shutdown"
