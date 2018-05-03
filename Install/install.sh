#! /bin/bash
PIHOME=/home/pi
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
GOPIGO3_DIR=$DEXTER_PATH/GoPiGo3
DEXTERSCRIPT=$DEXTER_PATH/lib/Dexter/script_tools

source $DEXTERSCRIPT/functions_library.sh

check_root_user() {
    if [[ $EUID -ne 0 ]]; then
        feedback "FAIL!  This script must be run as such: sudo ./install.sh"
        exit 1
    fi
    echo " "
}

install_dependencies() {

    # the sudo apt-get update is already
    # done by the script_tools installer in
    # update_gopigo.sh

    echo " "
    feedback "Installing Dependencies"
    feedback "======================="

    # for python3
    sudo apt-get install python3-pip python3-numpy python3-curtsies -y

    # for python2
    sudo apt-get install python-pip python-numpy python-curtsies -y

    feedback "Dependencies installed"
}

install_wiringpi() {
    # Check if WiringPi Installed

    # using curl piped to bash does not leave a file behind. no need to remove it
    # we can do either the curl - it works just fine
    # sudo curl https://raw.githubusercontent.com/DexterInd/script_tools/master/update_wiringpi.sh | bash
    # or call the version that's already on the SD card
    sudo bash $DEXTERSCRIPT/update_wiringpi.sh
    # done with WiringPi

    # remove wiringPi directory if present
    if [ -d wiringPi ]
    then
        sudo rm -r wiringPi
    fi
    # End check if WiringPi installed
    echo " "
}

enable_spi() {
    feedback "Removing blacklist from /etc/modprobe.d/raspi-blacklist.conf . . ."
    feedback "=================================================================="

    if grep -q "#blacklist spi-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
        echo "SPI already removed from blacklist"
    else
        sudo sed -i -e 's/blacklist spi-bcm2708/#blacklist spi-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
        echo "SPI removed from blacklist"
    fi

    #Adding in /etc/modules
    echo " "
    feedback "Adding SPI-dev in /etc/modules . . ."
    feedback "================================================"

    if grep -q "spi-dev" /etc/modules; then
        echo "spi-dev already there"
    else
        echo spi-dev >> /etc/modules
        echo "spi-dev added"
    fi
    echo " "
    feedback "Making SPI changes in /boot/config.txt . . ."
    feedback "================================================"

    if grep -q "#dtparam=spi=on" /boot/config.txt; then
        sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
        echo "SPI enabled"
    elif grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "SPI already enabled"
    else
        sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
        echo "SPI enabled"
    fi

    echo " "
}

# Enable GoPiGo3 Power Services in Systemd
# Make sure the gopigo3_power.py program will run at boot

# Update the Service File with the new directory path
SERVICEFILE=$GOPIGO3_DIR/Install/gpg3_power.service # This should be changed to the location of the sh file first.
SCRIPTFILE=$GOPIGO3_DIR/Install/gpg3_power.sh
SERVICECOMMAND=" ExecStart=/usr/bin/env bash "
# Remove line 8 from the service file, the default location of the Service File
sudo sed -i '6d' $SERVICEFILE
# Add new path and file name of gpg3_power.sh to the service file
sudo sed -i "6i $SERVICECOMMAND $SCRIPTFILE" $SERVICEFILE

check_root_user
install_dependencies
install_wiringpi
enable_spi
