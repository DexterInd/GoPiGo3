#!/bin/bash

# Removing old version of Node.js
sudo apt-get remove -y nodejs nodejs-legacy

# Installinv NVM
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.4/install.sh | bash