# GoPiGo3 BalanceBot

A self-balancing robot project using the GoPiGo3 with IMU sensor and IR remote control.

## Hardware Requirements

- GoPiGo3 robot
- Dexter Industries IMU sensor (connected to AD1 port, placed on right side with arrow pointing forward)
- Grove IR receiver (connected to AD2 port, placed across from the IMU)
- Dexter Industries Sensor Mounts (to secure sensors)
- Dexter Industries IR Remote Control

## Setup

### Virtual Environment Options

You have two options for setting up your Python environment:

#### Option 1: Reuse Existing GoPiGo3 Virtual Environment

If you already have a virtual environment with `mr-gopigo3` installed:

```bash
source /path/to/gopigo3/venv/bin/activate
pip install DI-Sensors
```

#### Option 2: Create a New Virtual Environment for This Project

```bash
python3 -m venv balancebot
source balancebot/bin/activate
pip install -r requirements.txt
```

## Running the Project

```bash
python BalanceBot.py
```

Follow the instructions printed in the terminal.

**Note:** This project works best on a carpeted surface!

## Controls

Use the Dexter Industries IR Remote Control to control the balancing robot.
