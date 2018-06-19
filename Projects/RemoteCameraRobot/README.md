# Remote Controlled GoPiGo3

In this project we remotely control a GoPiGo3 robot via a mobile device or a laptop.

![Imgur](http://i.imgur.com/sT2tHuPl.jpg)

## Requirements

We need the following components for this project:

* A [GoPiGo3](https://www.dexterindustries.com/gopigo3/) robot - it also includes the battery pack.
* A [Raspberry Pi](https://www.dexterindustries.com/raspberry-pi/).
* A [Pi Camera](https://www.dexterindustries.com/shop/raspberry-pi-camera/).
* A laptop or a mobile device (aka smartphone).

## Setting Up

In order to proceed the setup, make sure you have the `GoPiGo3` repository installed (not just cloned, but also installed) or that you have the latest version of `Raspbian For Robots`.

After going through the above paragraph, install the `Pi Camera` dependencies and `Flask` by running following command:
 ```
 sudo pip3 install -r requirements.txt
 ```

You should now have everything set up.

## Running it

Start the server by typing the following command:
```
python3 flask_server.py
```
It's going to take a couple of seconds for the server to fire up.
A port and address will be shown in there. By default, the port is set to `5000`.

If you have got `Raspbian For Robots` installed, then going to `http://dex.local:5000` address will be enough.
If you don't have `Raspbian For Robots`, then you'll need to see what's your interface's IP address.

Also, please make sure you have your mobile device / laptop on the same network as your `GoPiGo3`. Otherwise, you won't be able to access it.

## Setting Up to Run on Boot
You can run the server on boot so you don't have to run it manually.  Use the command
`install_startup.sh`
and this should start the flask server on boot.  You should be able to connect to the robot using "http://dex.local:5000" or if using the Cinch setup, you can use "http://10.10.10.10:5000"

You can setup Cinch, which will automatically setup a wifi access point, with the command
`sudo bash /home/pi/di_update/Raspbian_For_Robots/upd_script/wifi/cinch_setup.sh`
On reboot, connect to the WiFi service "Dex".

## YouTube Video

#### When loading `http://dex.local:5000` for the first time, click a couple of times on the screen without moving the mouse around, in order to enable the "joystick" functionality.

Here's a YouTube video of this project:

[![Alt text](https://img.youtube.com/vi/Tu_-Al6Smhg/0.jpg)](https://www.youtube.com/watch?v=Tu_-Al6Smhg)
