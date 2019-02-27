#! /bin/bash

# check the RPi version
RPI_VERSION=$(python3 -c "import auto_detect_rpi; print (auto_detect_rpi.getRPIGenerationCode())")

INTERFACE_FILE="none"
if [ "$RPI_VERSION" == "RPI1" ] || [ "$RPI_VERSION" == "RPI0" ]; then
    # use rpi1 interface config file
    INTERFACE_FILE="rpi1.cfg"
elif [ "$RPI_VERSION" == "RPI2" ] || [ "$RPI_VERSION" == "RPI3" ] || [ "$RPI_VERSION" == "RPI3B+" ] || [ "$RPI_VERSION" == "RPI3A+" ]; then
    # use rpi2 interface config file
    INTERFACE_FILE="rpi2.cfg"
fi

if [ "$INTERFACE_FILE" == "none" ]; then
    # unsupported RPI
    echo "Unsupported RPi version '$RPI_VERSION'. Please report to support@dexterindustries.com"
else
    echo "Using interface file '$INTERFACE_FILE' for RPi version '$RPI_VERSION'."

    # Read the path of the GoPiGo3 repository
    REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\GoPiGo3)")

    # Get the absolute path of the latest Firmware update
    FIRMWARE_FILE=$(sudo find "$REPO_PATH"/Firmware/ -maxdepth 1 -name *.bin)

    if [ "$FIRMWARE_FILE" == "" ]; then
        echo "Failed to find firmware file."
    else
        echo "Updating the GoPiGo3 Firmware with '$FIRMWARE_FILE'"

        # flash the firmware
        sudo openocd -f interface/$INTERFACE_FILE -c "transport select swd; set CHIPNAME at91samc20j18; source [find target/at91samdXX.cfg]; adapter_khz 50; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program $FIRMWARE_FILE verify; reset" -c "shutdown"
    fi
fi
