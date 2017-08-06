#!/bin/bash

# Removing old version of Node.js
sudo apt-get remove -y nodejs nodejs-legacy

# Installinv NVM
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh | bash

echo '!!!!'
echo 'Please, exit from this terminal session and do the login again. Once done, execute the installNodejs.sh script. Thanks.'
echo '!!!!'