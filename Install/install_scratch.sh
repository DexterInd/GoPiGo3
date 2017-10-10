echo "This script will install Scratch for GoPiGo3 on a standard Jessie Raspbian"


PIHOME=/home/pi
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
DEXTER=Dexter
ROBOT_FOLDER=GoPiGo3
LIB=lib
LIB_PATH=$PIHOME/$DEXTER/$LIB
DEXTERLIB_PATH=$LIB_PATH/$DEXTER
SCRATCH=Scratch_GUI
SCRATCH_PATH=$DEXTERLIB_PATH/$SCRATCH

if [ ! -d "$DEXTERLIB_PATH" ]
then
    echo "getting some helpers"
    # get the bash helper tools
    curl https://raw.githubusercontent.com/DexterInd/script_tools/master/install_script_tools.sh | bash
    pushd $DEXTERLIB_PATH/script_tools
    sudo python autodetect_setup.py install
    popd > /dev/null
fi
source $PIHOME/$DEXTER/lib/$DEXTER/script_tools/functions_library.sh

# feedback  "Installing some libraries"
# sudo apt-get install python-smbus python3-smbus

feedback "activating I2C"
sudo sed -i "/i2c-dev/d" /etc/modules
sudo echo "i2c-dev" >> /etc/modules
sudo sed -i "/dtparam=i2c_arm=on/d" /boot/config.txt
sudo echo "dtparam=i2c_arm=on" >> /boot/config.txt

feedback "Installing Scratch Environment"

create_folder $PIHOME/$DEXTER
create_folder $PIHOME/$DEXTER/$LIB
create_folder $PIHOME/$DEXTER/$LIB/$DEXTER
create_folder $PIHOME/$DEXTER/$LIB/$DEXTER/$SCRATCH

# installing scratch
pushd $LIB_PATH > /dev/null
delete_folder scratchpy
git clone https://github.com/DexterInd/scratchpy
cd scratchpy
sudo make install > /dev/null
popd > /dev/null


# Copy shortcut to desktop.
feedback "Installing Scratch on the desktop"
sudo cp $PIHOME/$DEXTER/$ROBOT_FOLDER/Software/Scratch/Local_Scratch_Start.desktop /home/pi/Desktop/Local_Scratch_Start.desktop

# Desktop shortcut permissions.
sudo chmod +x $PIHOME/Desktop/Local_Scratch_Start.desktop

# Make select_state, error_log, nohup.out readable and writable
sudo echo "GoPiGo3" >> $SCRATCH_PATH/selected_state
sudo touch $SCRATCH_PATH/error_log
sudo chmod 666 $SCRATCH_PATH/selected_state
sudo chmod 666 $SCRATCH_PATH/error_log

sudo cp  $PIHOME/$DEXTER/$ROBOT_FOLDER/Software/Scratch/new.sb $PIHOME/$DEXTER/$LIB/$DEXTER/$SCRATCH/new.sb

# transferring Scratch examples into proper Scratch folder
sudo rm  /usr/share/scratch/Projects/$ROBOT_FOLDER 2> /dev/null
sudo ln -s $PIHOME/$DEXTER/$ROBOT_FOLDER/Software/Scratch/Examples /usr/share/scratch/Projects/$ROBOT_FOLDER  2> /dev/null

feedback "You now have a Scratch icon on your desktop. Double clicking it will start Scratch with all the necessary configuration to control your GoPiGo3"
feedback "Please note that you cannot use Scratch from the menu or double click on a Scratch file to control your robot."
