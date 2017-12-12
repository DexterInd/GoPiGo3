# Installation file to make the Camera Robot start on boot.
# This will add the camerarobot start on boot to SystemD on Jessie/Stretch

sudo cp camerarobot.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/camerarobot.service
sudo systemctl daemon-reload
sudo systemctl enable camerarobot.service
