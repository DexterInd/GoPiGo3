#! /bin/bash

#rm "/home/pi/GoPiGo3_Firmware.bin"

#echo "Renaming '/home/pi/GoPiGo3 Firmware.bin' to '/home/pi/GoPiGo3_Firmware.bin'."
#mv "/home/pi/GoPiGo3 Firmware.bin" "/home/pi/GoPiGo3_Firmware.bin"

echo "Updating the GoPiGo3 Firmware with '/home/pi/Dexter/GoPiGo3/Firmware/GoPiGo3_Firmware.bin'."
sudo openocd -f interface/raspberrypi2-native.cfg -c "transport select swd; set CHIPNAME at91samc20j18; source [find target/at91samdXX.cfg]; adapter_khz 250; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program /home/pi/Dexter/GoPiGo3/Firmware/GoPiGo3_Firmware.bin verify; reset" -c "shutdown"
