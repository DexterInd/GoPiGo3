#! /bin/bash


# check if upgrade is needed
/usr/bin/python3 /home/pi/Dexter/GoPiGo3/Firmware/check_if_firmware_update_is_needed.py
if [ $? -eq 1 ]
then
  echo "Firmware is up to date and working properly."
  echo "Exiting firmware upgrade script file without changing anything."
  exit
else
    echo "Attempting to upgrade firmware."
fi

# check the RPi version
RPI_VERSION=$(python3 -c "import auto_detect_rpi; print (auto_detect_rpi.getRPIGenerationCode())")

INTERFACE_FILE="none"
if [ "$RPI_VERSION" == "RPI1" ] || [ "$RPI_VERSION" == "RPI0" ]; then
    # use rpi1 interface config file
    INTERFACE_FILE="rpi1.cfg"
elif [ "$RPI_VERSION" == "RPI2" ] || [ "$RPI_VERSION" == "RPI3" ] || [ "$RPI_VERSION" == "RPI3B+" ] || [ "$RPI_VERSION" == "RPI3A+" ]; then
    # use rpi2 interface config file
    INTERFACE_FILE="rpi2.cfg"
elif [ "$RPI_VERSION" == "RPI4" ]; then
    # use rpi4 interface config file
    echo "Flashing the firmware using a Pi4"
    INTERFACE_FILE="rpi4-sysfsgpio.cfg"
fi

if [ "$INTERFACE_FILE" == "none" ]; then
    # unsupported RPI
    echo "Unsupported RPi version '$RPI_VERSION'. Please report to support@dexterindustries.com"
else
    echo "Using interface file '$INTERFACE_FILE' for RPi version '$RPI_VERSION'."

    SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
    echo $SCRIPT_DIR
    # Get the absolute path of the latest Firmware update
    FIRMWARE_FILE=$(sudo find $SCRIPT_DIR -maxdepth 1 -name "*.bin")

    echo $FIRMWARE_FILE

    if [ "$FIRMWARE_FILE" == "" ]; then
        echo "Failed to find firmware file."
    else
        echo "Updating the GoPiGo3 Firmware with '$FIRMWARE_FILE'"

        if [ "$INTERFACE_FILE" == "rpi4-sysfsgpio.cfg" ]; then
            sudo openocd -f $SCRIPT_DIR/$INTERFACE_FILE -c "transport select swd; set CHIPNAME at91samc20j18; source [find target/at91samdXX.cfg]; adapter srst delay 100; adapter srst pulse_width 100" -c "init; targets; reset halt; program $FIRMWARE_FILE verify; reset" -c "shutdown"
        else
            # flash the firmware - P2 and Pi3
            sudo openocd -f $SCRIPT_DIR/$INTERFACE_FILE -c "transport select swd; set CHIPNAME at91samc20j18; source [find target/at91samdXX.cfg]; adapter_khz 50; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program $FIRMWARE_FILE verify; reset" -c "shutdown"
        fi

        echo $(python -c "import gopigo3;g=gopigo3.GoPiGo3();print('Success.')")
    fi
fi
