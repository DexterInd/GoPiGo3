#! /bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "Script ran without root privileges: not installing python packages."
fi

SCRIPTDIR="$(readlink -f $(dirname $0))"
echo $SCRIPTDIR
REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\GoPiGo3)")

#check if there's an argument on the command line
if [[ -f /home/pi/quiet_mode ]]
then
    quiet_mode=1
else
    quiet_mode=0
fi

if [[ "$quiet_mode" -eq "0" ]]
then
    echo "  _____            _                                "
    echo " |  __ \          | |                               "
    echo " | |  | | _____  _| |_ ___ _ __                     "
    echo " | |  | |/ _ \ \/ / __/ _ \ '__|                    "
    echo " | |__| |  __/>  <| ||  __/ |                       "
    echo " |_____/ \___/_/\_\ __\___|_| _        _            "
    echo " |_   _|         | |         | |      (_)           "
    echo "   | |  _ __   __| |_   _ ___| |_ _ __ _  ___  ___  "
    echo "   | | | '_ \ / _\ | | | / __| __| '__| |/ _ \/ __| "
    echo "  _| |_| | | | (_| | |_| \__ \ |_| |  | |  __/\__ \ "
    echo " |_____|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/ "
    echo "                                                    "
    echo "                                                    "
fi

echo "   ____       ____  _  ____      _____ "
echo "  / ___| ___ |  _ \(_)/ ___| ___|___ / "
echo " | |  _ / _ \| |_) | | |  _ / _ \ |_ \ "
echo " | |_| | (_) |  __/| | |_| | (_) |__) |"
echo "  \____|\___/|_|   |_|\____|\___/____/ "
echo "                                       "

echo ""
echo "Welcome to GoPiGo3 Installer."

echo ""

# Enable GoPiGo3 Power Services in Systemd
# Make sure the gopigo3_power.py program will run at boot

# Update the Service File with the new directory path
SERVICEFILE=$REPO_PATH/Install/gpg3_power.service # This should be changed to the location of the sh file first.
SCRIPTFILE=$REPO_PATH/Install/gpg3_power.sh
SERVICECOMMAND=" ExecStart=/usr/bin/env bash "
# Remove line 8 from the service file, the default location of the Service File
sudo sed -i '6d' $SERVICEFILE
# Add new path and file name of gpg3_power.sh to the service file
sudo sed -i "6i $SERVICECOMMAND $SCRIPTFILE" $SERVICEFILE

# Install the system services
sudo cp $REPO_PATH/Install/gpg3_power.service /etc/systemd/system

sudo chmod 644 /etc/systemd/system/gpg3_power.service
sudo systemctl daemon-reload


sudo systemctl enable gpg3_power.service

echo ""
sudo bash $REPO_PATH/Firmware/openocd/install_openocd_compiled.sh

# Adding in /etc/modules
# this is not needed with Jessie and leads to a FAILED error at boot
# (boot does work though)
# echo ""
# if grep -q "spi-dev" /etc/modules; then
#     echo "spi-dev already present in /etc/modules"
# else
#     echo spi-dev >> /etc/modules
#     echo "spi-dev added to /etc/modules"
# fi

# Enable SPI
echo ""
if grep -q "#dtparam=spi=on" /boot/config.txt; then
    sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
    echo "SPI enabled"
elif grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "SPI already enabled"
else
    sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
    echo "SPI enabled"
fi

echo ""
cd $REPO_PATH/Software/Python/
python setup.py install
python3 setup.py install

# module for interfacing with the keyboard
pip3 install curtsies
pip3 install numpy
pip3 install python-periphery
pip install curtsies
pip install numpy
pip install python-periphery

echo ""
echo "Installation complete"
echo "Please reboot to make settings take effect"
