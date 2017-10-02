#!/bin/bash
#
# Remove NPM / NodeJS / NVM from the current user
#

read -p "This operation will remove NPM, Node.js and NVM from your user profile, are you sure? [Y/N] " answer
if [[ $answer = [Yy] ]] ; then
    echo "Executing..."
    rm -rf $NVM_DIR ~/.npm ~/.bower && unset NVM_DIR && source ~/.bashrc
    echo "Done."

    bash -l
fi