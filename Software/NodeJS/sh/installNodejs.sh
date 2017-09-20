#!/bin/bash

# Loading NVM
source ~/.nvm/nvm.sh
source ~/.profile
source ~/.bashrc

# Installing stable version of Node.js
nvm install 8.5.0

# Validating installation
echo "❤ Node.js version"
node --version
echo "❤ NPM version"
npm --version