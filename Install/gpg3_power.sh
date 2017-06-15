#! /usr/bin/env bash
# This script is used to detect if GPG3 connected and run the gopigo3_power.py
# This script is called by gpg3_power.service

# These lines are specific to the GoPiGo3
SCRIPTDIR="$(readlink -f $(dirname $0))"
echo $SCRIPTDIR
REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\GoPiGo3)")


# Check if gopigo3_power.py is running.
SERVICE='gopigo3_power.py'
# To be able to do an update without crapping out, we need to have power management on.  So let's directly turn it on.
if ps ax | grep -v grep | grep $SERVICE > /dev/null
then
    echo "$SERVICE service running."
else
    echo "$SERVICE is not running"
    # Run the gopigo3_power.py if GPG3 detected
    sudo python $REPO_PATH/Software/gopigo3_power.py
    echo "$SERVICE started."
fi