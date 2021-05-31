#! /bin/bash

PIHOME=/home/pi
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
GOPIGO3_DIR=$DEXTER_PATH/GoPiGo3
DEXTERSCRIPT=$DEXTER_PATH/lib/Dexter/script_tools

# the top-level module name of each package
# used for identifying present packages
REPO_PACKAGE=gopigo3

# the following option specifies which GoPiGo3 github branch to use
selectedbranch="master"

##############################################
######## Parse Command Line Arguments ########
##############################################

# called way down bellow
check_if_run_with_pi() {
  ## if not running with the pi user then exit
  if [ $(id -ur) -ne $(id -ur pi) ]; then
    echo "GoPiGo3 installer script must be run with \"pi\" user. Exiting."
    exit 6
  fi
}

# called way down below
parse_cmdline_arguments() {

  # whether to install the dependencies or not (avrdude, apt-get, wiringpi, and so on)
  installdependencies=true
  updaterepo=true
  install_rfrtools=true
  install_pkg_rfrtools=true
  install_rfrtools_gui=true

  # the following 3 options are mutually exclusive
  systemwide=true
  userlocal=false
  envlocal=false
  usepython2exec=true
  usepython3exec=true

  # selectedbranch=master
  # "selectedbranch" variable can be found up top in the code

  declare -ga rfrtools_options=("--system-wide")
  # iterate through bash arguments
  for i; do
    case "$i" in
      --no-dependencies)
        installdependencies=false
        ;;
      --no-update-aptget)
        updaterepo=false
        ;;
      --bypass-rfrtools)
        install_rfrtools=false
        ;;
      --bypass-python-rfrtools)
        install_pkg_rfrtools=false
        ;;
      --bypass-gui-installation)
        install_rfrtools_gui=false
        ;;
      --user-local)
        userlocal=true
        systemwide=false
        declare -ga rfrtools_options=("--user-local")
        ;;
      --env-local)
        envlocal=true
        systemwide=false
        declare -ga rfrtools_options=("--env-local")
        ;;
      --system-wide)
        ;;
      develop|feature/*|hotfix/*|fix/*|DexterOS*|v*)
        selectedbranch="$i"
        ;;
    esac
  done

  # show some feedback on the console
  if [ -f $DEXTERSCRIPT/functions_library.sh ]; then
    source $DEXTERSCRIPT/functions_library.sh
    # show some feedback for the GoPiGo3
    if [[ quiet_mode -eq 0 ]]; then
      echo "  _____            _                                ";
      echo " |  __ \          | |                               ";
      echo " | |  | | _____  _| |_ ___ _ __                     ";
      echo " | |  | |/ _ \ \/ / __/ _ \ '__|                    ";
      echo " | |__| |  __/>  <| ||  __/ |                       ";
      echo " |_____/ \___/_/\_\\\__\___|_|          _            ";
      echo " |_   _|         | |         | |      (_)           ";
      echo "   | |  _ __   __| |_   _ ___| |_ _ __ _  ___  ___  ";
      echo "   | | | '_ \ / _\ | | | / __| __| '__| |/ _ \/ __| ";
      echo "  _| |_| | | | (_| | |_| \__ \ |_| |  | |  __/\__ \ ";
      echo " |_____|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/ ";
      echo "                                                    ";
      echo "                                                    ";
      echo "   ____       ____  _  ____      _____ "
      echo "  / ___| ___ |  _ \(_)/ ___| ___|___ / "
      echo " | |  _ / _ \| |_) | | |  _ / _ \ |_ \ "
      echo " | |_| | (_) |  __/| | |_| | (_) |__) |"
      echo "  \____|\___/|_|   |_|\____|\___/____/ "
      echo "                                       "
    fi

    feedback "Welcome to GoPiGo3 Installer."
  else
    echo "Welcome to GoPiGo3 Installer."
  fi

  echo "Updating GoPiGo3 for $selectedbranch branch with the following options:"
  ([[ $installdependencies = "true" ]] && echo "  --no-dependencies=false") || echo "  --no-dependencies=true"
  ([[ $updaterepo = "true" ]] && echo "  --no-update-aptget=false") || echo "  --no-update-aptget=true"
  ([[ $install_rfrtools = "true" ]] && echo "  --bypass-rfrtools=false") || echo "  --bypass-rfrtools=true"
  ([[ $install_pkg_rfrtools = "true" ]] && echo "  --bypass-python-rfrtools=false") || echo "  --bypass-python-rfrtools=true"
  ([[ $install_rfrtools_gui = "true" ]] && echo "  --bypass-gui-installation=false") || echo "  --bypass-gui-installation=true"
  echo "  --user-local=$userlocal"
  echo "  --env-local=$envlocal"
  echo "  --system-wide=$systemwide"

  # create rest of list of arguments for rfrtools call
  rfrtools_options+=("$selectedbranch")
  [[ $usepython2exec = "true" ]] && rfrtools_options+=("--use-python2-exe-too")
  [[ $usepython3exec = "true" ]] && rfrtools_options+=("--use-python3-exe-too")
  [[ $updaterepo = "true" ]] && rfrtools_options+=("--update-aptget")
  [[ $installdependencies = "true" ]] && rfrtools_options+=("--install-deb-deps")
  [[ $install_pkg_rfrtools = "true" ]] && rfrtools_options+=("--install-python-package")
  [[ $install_rfrtools_gui = "true" ]] && rfrtools_options+=("--install-gui")

  echo "Using \"$selectedbranch\" branch"
  echo "Options used for RFR_Tools script: \"${rfrtools_options[@]}\""
}

#################################################
########## Cloning GoPiGo3 & RFR_Tools ##########
#################################################

# called in <<install_rfrtools_repo>>
check_dependencies() {
  command -v git >/dev/null 2>&1 || { echo "This script requires \"git\" but it's not installed. Error occurred with RFR_Tools installation." >&2; exit 1; }
  if [[ $usepython2exec = "true" ]]; then
    command -v python2 >/dev/null 2>&1 || { echo "Executable \"python2\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 2; }
    command -v pip2 >/dev/null 2>&1 || { echo "Executable \"pip2\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 3; }
  fi
  if [[ $usepython3exec = "true" ]]; then
    command -v python3 >/dev/null 2>&1 || { echo "Executable \"python3\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 4; }
    command -v pip3 >/dev/null 2>&1 || { echo "Executable \"pip3\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 5; }
  fi

  if [[ ! -f $DEXTERSCRIPT/functions_library.sh ]]; then
    echo "script_tools didn\'t get installed. Enable the installation of dependencies with RFR_Tools.'"
    exit 8
  fi
}

# called way down below
install_rfrtools_repo() {

  # if rfrtools is not bypassed then install it
  if [[ $install_rfrtools = "true" ]]; then
    curl --silent -kL https://raw.githubusercontent.com/DexterInd/RFR_Tools/$selectedbranch/scripts/install_tools.sh > $PIHOME/.tmp_rfrtools.sh
    echo "Installing RFR_Tools. This might take a while.."
    bash $PIHOME/.tmp_rfrtools.sh ${rfrtools_options[@]} # > /dev/null
    ret_val=$?
    rm $PIHOME/.tmp_rfrtools.sh
    if [[ $ret_val -ne 0 ]]; then
      echo "RFR_Tools failed installing with exit code $ret_val. Exiting."
      exit 7
    fi
    echo "Done installing RFR_Tools"
  fi

  # check if all deb packages have been installed with RFR_Tools
  check_dependencies

  source $DEXTERSCRIPT/functions_library.sh
}

# called way down bellow
clone_gopigo3() {
  # $DEXTER_PATH is still only available for the pi user
  # shortly after this, we'll make it work for any user
  sudo mkdir -p $DEXTER_PATH
  sudo chown pi:pi -R $DEXTER_PATH
  cd $DEXTER_PATH
  # it's simpler and more reliable (for now) to just delete the repo and clone a new one
  # otherwise, we'd have to deal with all the intricacies of git
  sudo rm -rf $GOPIGO3_DIR
  git clone --quiet --depth=1 -b $selectedbranch https://github.com/DexterInd/GoPiGo3.git
  cd $GOPIGO3_DIR
}

################################################
##### Install Python Packages & Services #######
################################################

# called by <<install_python_pkgs_and_dependencies>>
install_python_packages() {
  [[ $systemwide = "true" ]] && [[ $usepython2exec = "true" ]] && sudo python2 setup.py install 
  [[ $systemwide = "true" ]] && [[ $usepython3exec = "true" ]] && sudo python3 setup.py install
  [[ $userlocal = "true" ]]  && [[ $usepython2exec = "true" ]] && python2 setup.py install --user 
  [[ $userlocal = "true" ]]  && [[ $usepython3exec = "true" ]] && python3 setup.py install --user
  [[ $envlocal = "true" ]]   && [[ $usepython2exec = "true" ]] && python2 setup.py install
  [[ $envlocal = "true" ]]   && [[ $usepython3exec = "true" ]] && python3 setup.py install
}

# called by <<install_python_pkgs_and_dependencies>>
remove_python_packages() {
  # the 1st and only argument
  # takes the name of the package that needs to removed
  rm -f $PIHOME/.pypaths

  # get absolute path to python package
  # saves output to file because we want to have the syntax highlight working
  # does this for both root and the current user because packages can be either system-wide or local
  # later on the strings used with the python command can be put in just one string that gets used repeatedly
  if [[ $usepython2exec = "true" ]]; then 
    python2 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
    sudo python2 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  fi
  if [[ $usepython3exec = "true" ]]; then
    python3 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
    sudo python3 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  fi

  # removing eggs for $1 python package
  # ideally, easy-install.pth needs to be adjusted too
  # but pip seems to know how to handle missing packages, which is okay
  while read path;
  do
    if [ ! -z "${path}" -a "${path}" != " " ]; then
      echo "Removing ${path} egg"
      sudo rm -f "${path}"
    fi
  done < $PIHOME/.pypaths
}

# called way down bellow
install_python_pkgs_and_dependencies() {
  # installing dependencies if required
  if [[ $installdependencies = "true" ]]; then
    pushd $GOPIGO3_DIR/Install > /dev/null
    sudo bash ./install.sh
    popd > /dev/null
  fi

  feedback "Removing \"$REPO_PACKAGE\" to make space for the new one"
  remove_python_packages "$REPO_PACKAGE"

  # installing the package itself
  pushd $GOPIGO3_DIR/Software/Python > /dev/null
  install_python_packages
  popd > /dev/null

  # install control panel on desktop
  if [[ -d $PIHOME/Desktop ]]; then
    cp $GOPIGO3_DIR/Software/Python/Examples/Control_Panel/gopigo3_control_panel.desktop $PIHOME/Desktop/gopigo3_control_panel.desktop
  fi

  # install openocd
  echo "Installing OpenOCD for GoPiGo3"
  curl --silent https://raw.githubusercontent.com/DexterInd/openocd/master/openocd_install.sh | bash
}

# called way down bellow
install_gopigp3_power_service() {
  # Install the system services
  sudo cp $GOPIGO3_DIR/Install/gpg3_power.service /etc/systemd/system
  sudo chmod 644 /etc/systemd/system/gpg3_power.service
  sudo systemctl daemon-reload
  sudo systemctl enable gpg3_power.service
  sudo systemctl start gpg3_power.service
}

################################################
######## Call all functions - main part ########
################################################

check_if_run_with_pi

parse_cmdline_arguments "$@"
install_rfrtools_repo

clone_gopigo3
install_python_pkgs_and_dependencies
install_gopigp3_power_service

exit 0
