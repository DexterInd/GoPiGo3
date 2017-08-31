echo "Checking if code name distribution is jessie"
CODE_NAME_DIST="$(lsb_release --codename)"
if [[ $CODE_NAME_DIST != *"jessie" ]]; then
  echo "Code name distribution mismatch"
  echo "Found "$CODE_NAME_DIST
  exit 1
else
  echo "Found jessie distribution"
fi

echo "Adding repository location for UV4L"
curl -s http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add - > /dev/null
if grep -q "[# ]*deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main" /etc/apt/sources.list
then
    sed -i '/deb http:\/\/www\.linux-projects\.org\/listing\/uv4l_repo\/raspbian\/ jessie main/s/^#//' /etc/apt/sources.list
else
    echo -e "deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main" >> /etc/apt/sources.list
fi


echo "Updating repository"
apt-get update > /dev/null

echo "Installing UV4L drivers"
apt-get install uv4l uv4l-raspicam
apt-get install uv4l-raspicam-extras

echo "Copying configs for UV4L drivers"
cp uv4l-raspicam.conf /etc/uv4l/uv4l-raspicam.conf

echo "Restarting UV4L service"
service uv4l_raspicam restart

echo "Installing Flask"
apt-get install python3-flask
