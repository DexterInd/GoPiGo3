#!/bin/bash
#
# - Install NPM / NodeJS / NVM for the current user

function realpath()
{
    f=$@
    if [ -d "$f" ]; then
        base=""
        dir="$f"
    else
        base="/$(basename "$f")"
        dir=$(dirname "$f")
    fi
    dir=$(cd "$dir" && /bin/pwd)
    echo "$dir$base"
}

if [ "$(id -u)" == "0" ]; then
   echo "This script cannot be run as sudo" 1>&2
   exit 1
fi

read -p "This operation will install NPM, Node.js and NVM for the current user profile, do you want to proceed? [Y,N] " answer
if [[ $answer = [Yy] ]] ; then

    # Installing NVM
    curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.4/install.sh | bash

    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

    # Installing Node.js
    nvm install 8.5.0

    # Validating installation
    echo "❤ Node.js version"
    node --version
    echo "❤ NPM version"
    npm --version

    echo
    echo
    echo "Done, you can now use Node.js on your device."
    echo "If you need to build the current library run 'npm install' inside the NodeJS folder"
    echo "otherwise you can already start using it including the npm package (node-gopigo3) in your application."
    echo
    echo "For any other hint please check the repository."
    echo "Bye!"
    echo
    echo

    bash -l
fi