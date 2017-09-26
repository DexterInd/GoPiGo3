# Check for a GoPiGo3 directory under "Dexter" folder.  If it doesn't exist, create it.
PIHOME=/home/pi
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
curl --silent https://raw.githubusercontent.com/DexterInd/script_tools/master/install_script_tools.sh | bash

# needs to be sourced from here when we call this as a standalone
source /home/pi/$DEXTER/lib/$DEXTER/script_tools/functions_library.sh

GOPIGO3_DIR=$DEXTER_PATH/GoPiGo3
if folder_exists "$GOPIGO3_DIR" ; then
    echo "GoPiGo3 Directory Exists"
    cd $DEXTER_PATH/GoPiGo3    # Go to directory
    sudo git fetch origin       # Hard reset the git files
    sudo git reset --hard  
    sudo git merge origin/master
    # change_branch $BRANCH
else
    cd $DEXTER_PATH
    git clone https://github.com/DexterInd/GoPiGo3
    cd GoPiGo3
    # change_branch $BRANCH  # change to a branch we're working on, if we've defined the branch above.
fi

sudo bash /home/pi/Dexter/GoPiGo3/Install/install.sh
