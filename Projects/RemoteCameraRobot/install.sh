#!/usr/bin/env bash

# check https://www.linux-projects.org/uv4l/installation/ for more information
# jessie/wheezy versions of UV4L are no longer maintained and hence
# it's recommended to run this on a stretch

echo "Checking if code name distribution is jessie/stretch"
OS_CODENAME="$(lsb_release --codename --short)"
if [[ $OS_CODENAME != "stretch" && $OS_CODENAME != "jessie" ]]; then
  echo "Code name distribution mismatch"
  echo "Only Stretch and Jessie version are supported - soon enough, Jessie will no longer be supported as UV4L no longer maintains the project for Jessie"
  exit 1
fi

echo "Found $OS_CODENAME distribution"

# for stretch and jessie there are different sources
if [[ $OS_CODENAME == "stretch" ]]; then
  RELATIVE_PATH_SRC="stretch"
else
  RELATIVE_PATH_SRC=""
fi

echo "Adding repository location for UV4L"
curl -s http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add - > /dev/null
echo -e "deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/$RELATIVE_PATH_SRC $OS_CODENAME main" >> /etc/apt/sources.list

echo "Updating repository"
apt-get update

echo "Installing UV4L drivers"
apt-get -y install uv4l uv4l-raspicam
apt-get -y install uv4l-raspicam-extras
apt-get -y install uv4l-server

echo "Copying configs for UV4L drivers"
cp uv4l-raspicam.conf /etc/uv4l/uv4l-raspicam.conf

echo "Restarting UV4L service"
service uv4l_raspicam restart

echo "Installing Flask"
apt-get -y install python3-flask wiringpi
