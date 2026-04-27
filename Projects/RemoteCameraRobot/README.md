# Remote Controlled GoPiGo3

In this project we remotely control a GoPiGo3 robot via a mobile device or a laptop.

![Imgur](http://i.imgur.com/sT2tHuPl.jpg)

## Setup

### Virtual Environment Options

You have two options for setting up your Python environment:

#### Option 1: Reuse Existing GoPiGo3 Virtual Environment

If you already have a virtual environment with `mr-gopigo3` installed:

```bash
source /path/to/gopigo3/venv/bin/activate
pip install flask==3.1.3 werkzeug==3.1.6 picamera==1.13
```

#### Option 2: Create a New Virtual Environment for This Project

```bash
python3 -m venv remotecamerarobot
source remotecamerarobot/bin/activate
pip install -r requirements.txt
```

### Running the Server

Start the server by typing the following command:
```bash
python remote_robot.py
```

It's going to take a couple of seconds for the server to fire up.
The web app is set to port `5000` whereas the video stream is found at port `5001`.

Access the web interface at:
- With Raspbian For Robots: `http://dex.local:5000`
- Otherwise: `http://<raspberry-pi-ip>:5000`

Make sure your mobile device/laptop is on the same network as your GoPiGo3.

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
python3 remote_robot.py
```
It's going to take a couple of seconds for the server to fire up.
The web app is set to port `5000` whereas the video stream is found at port `5001`.

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

[![Alt text](https://img.youtube.com/vi/jyg_nt28ktk/0.jpg)](https://youtu.be/jyg_nt28ktk)
