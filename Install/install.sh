#! /bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 
    exit 1
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

# Make sure the gopigo3_power.py program will run at boot
# Add 'sudo python /home/pi/Dexter/GoPiGo3/Software/gopigo3_power.py &' to /etc/rc.local
echo ""
if grep -q "sudo python /home/pi/Dexter/GoPiGo3/Software/gopigo3_power.py &" /etc/rc.local; then
    echo "'sudo python /home/pi/Dexter/GoPiGo3/Software/gopigo3_power.py &' already present in /etc/rc.local"
else
    # allow appending to rc.local
    sudo chmod 777 /etc/rc.local
    
    # remove 'exit 0'
    sudo sed -i '/exit/d' /etc/rc.local
    
    # add 'sudo python /home/pi/Dexter/GoPiGo3/Software/gopigo3_power.py &'
    echo "sudo python /home/pi/Dexter/GoPiGo3/Software/gopigo3_power.py &" >> /etc/rc.local
    
    # add 'exit 0' back in
    echo "exit 0" >> /etc/rc.local
    
    echo "'sudo python /home/pi/Dexter/GoPiGo3/Software/gopigo3_power.py &' added to /etc/rc.local"
fi

echo ""
sudo bash $REPO_PATH/Firmware/openocd/install_openocd_compiled.sh

# Adding in /etc/modules
echo ""
if grep -q "spi-dev" /etc/modules; then
    echo "spi-dev already present in /etc/modules"
else
    echo spi-dev >> /etc/modules
    echo "spi-dev added to /etc/modules"
fi

# Enable SPI
echo ""
if grep -q "#dtparam=spi=on" /boot/config.txt; then
    sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
    echo "SPI enabled"
elif grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "SPI already enabled"
else
    echo 'dtparam=spi=on' >> /boot/config.txt
    echo "SPI enabled"
fi

echo ""
cd $REPO_PATH/Software/Python/
sudo python setup.py install
sudo python3 setup.py install

echo ""
echo "Installation complete"
echo "Please reboot to make settings take effect"
