#!/usr/bin/env bash

# check https://www.linux-projects.org/uv4l/installation/ for more information
# jessie/wheezy versions of UV4L are no longer maintained and hence
# it's recommended to run this on a stretch

echo "Checking if code name distribution is jessie/stretch"
OS_CODENAME="$(lsb_release --codename --short)"
if [[ $OS_CODENAME != "stretch" ]]; then
  echo "Code name distribution mismatch"
  echo "Only Stretch is supported - older versions like Jessie or Wheezy are no longer maintained"
  exit 1
fi

echo "Found $OS_CODENAME distribution"

echo "Adding repository location for UV4L"
curl -s http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add - > /dev/null
if grep -q "[# ]*deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" /etc/apt/sources.list
then
    sed -i '/deb http:\/\/www\.linux-projects\.org\/listing\/uv4l_repo\/raspbian\/stretch stretch main/s/^#//' /etc/apt/sources.list
else
    echo -e "deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" >> /etc/apt/sources.list
fi


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
