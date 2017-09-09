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
    $( dirname "$0" )/sh/installNvm.sh && source ~/.bashrc && $( dirname "$0" )/sh/installNodejs.sh
    echo
    echo
    echo "Done, you can now use Node.js on your device."
    echo "If you need to build the current library run 'npm install' inside '$( dirname "$0" )' otherwise you can already start using it"
    echo "including the npm package (node-gopigo3) in your application."
    echo
    echo "For any other hint please go to the repository."
    echo "Bye!"
    echo
    echo
fi