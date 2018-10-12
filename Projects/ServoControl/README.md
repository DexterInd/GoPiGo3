# Servo Control Panel

With this program you can test the servo functionality on the GoPiGo3. The available keys are described when the program is launched.

The script can be launched this way:
```
python run_this.py
```

# The Control Panel

The control panel the user sees when the program is launched can be rendered with formatted-text this way:
```
Press the following keys to run the features of the GoPiGo3.
To rotate the servos, make sure you have a fresh set of batteries powering the GoPiGo3.
Use servos that can turn to 180 degrees as some have difficulties doing it.

[key <F1>    ] :  Turn SERVO1 completely to 0 degrees
[key <F2>    ] :  Turn SERVO1 completely to 180 degrees
[key <F5>    ] :  Turn SERVO2 completely to 0 degrees
[key <F6>    ] :  Turn SERVO2 completely to 180 degrees
[key a       ] :  Turn SERVO1 towards 0 degrees incrementely
[key d       ] :  Turn SERVO1 towords 180 degrees incrementely
[key <LEFT>  ] :  Turn SERVO2 towards 0 degrees incrementely
[key <RIGHT> ] :  Turn SERVO2 towards 180 degrees incrementely
[key <SPACE> ] :  Turn off power supply to both servos
[key <ESC>   ] :  Exit
```