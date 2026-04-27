# Basic Robot Control Panel

With this program you can test a variety of functions of the GoPiGo3 ranging from built-in LEDs to moving the robot around. The available keys are described when the program is launched.

## Setup

### Virtual Environment Options

You have two options for setting up your Python environment:

#### Option 1: Reuse Existing GoPiGo3 Virtual Environment

If you already have a virtual environment with `mr-gopigo3` installed:

```bash
source /path/to/gopigo3/venv/bin/activate
pip install curtsies
```

#### Option 2: Create a New Virtual Environment for This Project

```bash
python3 -m venv basicrobocontrol
source basicrobocontrol/bin/activate
pip install -r requirements.txt
```

## Running the Program

The script can be launched this way:
```bash
python run_this.py
```

# The Control Panel

The control panel the user sees when the program is launched can be rendered with formatted-text this way:
```
Press the following keys to run the features of the GoPiGo3.
To move the motors, make sure you have a fresh set of batteries powering the GoPiGo3.

[key w       ] :  Move the GoPiGo3 forward
[key s       ] :  Move the GoPiGo3 backward
[key a       ] :  Turn the GoPiGo3 to the left
[key d       ] :  Turn the GoPiGo3 to the right
[key <SPACE> ] :  Stop the GoPiGo3 from moving
[key <F1>    ] :  Drive forward for 10 centimeters
[key <F2>    ] :  Drive forward for 10 inches
[key <F3>    ] :  Drive forward for 360 degrees (aka 1 wheel rotation)
[key 1       ] :  Turn ON/OFF left blinker of the GoPiGo3
[key 2       ] :  Turn ON/OFF right blinker of the GoPiGo3
[key 3       ] :  Turn ON/OFF both blinkers of the GoPiGo3
[key 8       ] :  Turn ON/OFF left eye of the GoPiGo3
[key 9       ] :  Turn ON/OFF right eye of the GoPiGo3
[key 0       ] :  Turn ON/OFF both eyes of the GoPiGo3
[key <INSERT>] :  Change the eyes' color on the go
[key <ESC>   ] :  Exit
```