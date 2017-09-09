#!/bin/bash

# Loading NVM
. ~/.nvm/nvm.sh
. ~/.profile
. ~/.bashrc

# Installing stable version of Node.js
nvm install node v8.4.0

# Validating installation
echo "❤ Node.js version"
node --version
echo "❤ NPM version"
npm --version