# 1 Detect if we are on a GoPiGo3
# 2 Detect if we have Wifi connection
# 3 Throw a yellow-orangey LED or turn it off


# If detected_robot exists and it contains GoPiGo3, or 
# if it doesn't exist at all on standalone Raspbian
if [ -f "/home/pi/Dexter/detected_robot.txt" ] && grep -q GoPiGo3 /home/pi/Dexter/detected_robot.txt  || [  ! -f "/home/pi/Dexter/detected_robot.txt" ]
then
    if iwgetid --scheme
    then
        python -c "import gopigo3;GPG=gopigo3.GoPiGo3();GPG.set_led(GPG.LED_WIFI,5,5,0)"
    else
        python -c "import gopigo3;GPG=gopigo3.GoPiGo3();GPG.set_led(GPG.LED_WIFI,0,0,0)"
    fi
fi
