#!/bin/bash

# Loading NVM
. ~/.nvm/nvm.sh
. ~/.profile
. ~/.bashrc

# Installing stable version of Node.js
nvm install node stable

# Validating installation
echo "❤ Node.js version"
node --version
echo "❤ NPM version"
npm --version

echo '!!!!'
echo 'Please, exit from this terminal session and do the login again, then you will be able to use Node.js, thanks.'
echo '!!!!'