#! /bin/bash

# Read the path of the GoPiGo3 repository
REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\GoPiGo3)")

# Get the absolute path of the latest Firmware update
FIRMWARE_FILE=$(sudo find "$REPO_PATH"/Firmware/ -maxdepth 1 -name *.bin)

echo "Updating the GoPiGo3 Firmware with '$FIRMWARE_FILE'."

# check the RPi version
RPI_VERSION=$(python -c "import auto_detect_rpi; print auto_detect_rpi.getRPIGenerationCode()")
# set default to RPi 1 interface config file
INTERFACE_FILE="rpi1.cfg"
if [ "$RPI_VERSION" == "RPI2" ] || [ "$RPI_VERSION" == "RPI3" ] || [ "$RPI_VERSION" == "RPI3B+" ]; then
    # use RPi 2 interface config file
    INTERFACE_FILE="rpi2.cfg"
fi
echo "Using interface file '$INTERFACE_FILE'"

# flash the firmware
sudo openocd -f interface/$INTERFACE_FILE -c "transport select swd; set CHIPNAME at91samc20j18; source [find target/at91samdXX.cfg]; adapter_khz 50; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program $FIRMWARE_FILE verify; reset" -c "shutdown"
