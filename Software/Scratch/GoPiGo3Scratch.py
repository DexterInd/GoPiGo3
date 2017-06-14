from __future__ import print_function
from __future__ import division
from builtins import input

import scratch
import re
import string
import math
import time
import sys
import easygopigo3 as easy
import os # needed to create folders
try:
    sys.path.insert(0, '/home/pi/Dexter/PivotPi/Software/Scratch/')
    import PivotPiScratch
    pivotpi_available=True
except:
    pivotpi_available=False

## Add what's required to have modal popup windows
## and handle crashes if any
from Tkinter import *
import tkMessageBox
import atexit

    
def error_box(in_string):
    '''
    Code to generate popup window
    '''
    window = Tk()
    window.wm_withdraw()

    #message at x:200,y:200
    window.geometry("1x1+"+str(window.winfo_screenwidth()//2)+"+"+str(window.winfo_screenheight()//2))
    tkMessageBox.showerror(title="error",message=in_string,parent=window)

@atexit.register
def cleanup():
    '''
    Stop BrickPi3 and print out error msg
    if I can figure out how to differentiate between normal exit and crash
    then I'll consider having a popup window here.
    '''
    try:
        gpg.reset_all() 
        # we want the gopigo3 to stop if gopigo3Scratch.py crashes
    except:
        pass
    print ("Scratch Interpreter closed")


##################################################################
# GLOBAL VARIABLES
##################################################################

# Set to 1 to have debugging information printed out
# Set to 0 to go into quiet mode
en_debug = 1
success_code = "SUCCESS"

try:
    gpg = easy.EasyGoPiGo3()
    print("GoPiGo3 Detected and Connected")

except gpg.FirmwareVersionError as error:
    error_box("The GoPiGo3 needs to be updated (see DI Update Software)")
    print ("Scratch Interpreter closed: {}".format(error.args[0]))
    sys.exit()
except IOError as error:
    error_box("Connection Error: {}".format(error.args[0]))
    print(error.args[0], ". Exiting...")
    sys.exit()
except Exception as e:
    error_box("Unknown Error, closing Scratch Interpreter")
    print("Unknown Error: {}".format(e))
    sys.exit()
    
try:
    distance_sensor = easy.DistanceSensor(gpg)
    print ("Distance sensor is detected")
except:
    distance_sensor = None

defaultCameraFolder="/home/pi/Desktop/"
cameraFolder = defaultCameraFolder

# sensor values as sent to Scratch to display
sensors = {}

# known sensors per port
# I2C not being tracked as not needed
known_sensors = {
    "AD1": None,
    "AD2": None,
    "Serial:": None,
    "Servo1": None,
    "Servo2": None
}

eye_colors = {
"white":  (255,255,255),
"yellow": (255,255,0),
"fuchsia":(255,0,255),
"red":(255,0,0),
"read":(255,0,0),
"silver":  (192,192,192),
"gray": (128,128,128),
"grey": (128,128,128),
"olive":(128,128,0),
"purple":  (128,0,128),
"maroon": (128,0,0),
"maron": (128,0,0),
"aqua":(0,255,255),
"lime":    (0,255,0),
"teal":   (0,128,128),
"teel":   (0,128,128),
"green":  (0,128,0),
"blue": (0,0,255),
"navy":(0,0,128),
"black": (0,0,0)
}

regex_accepted_colors = ""
for k in eye_colors:
    regex_accepted_colors = regex_accepted_colors + k
    regex_accepted_colors = regex_accepted_colors + "|"


# Keep these in sync with the grouping done with regex
DRIVE_GROUP = 1
DRIVE_DIRECTION_GROUP = DRIVE_GROUP+1
DRIVE_DISTANCE_GROUP = DRIVE_DIRECTION_GROUP+3
DRIVE_CM_GROUP = DRIVE_DISTANCE_GROUP+2
DRIVE_INCHES_GROUP = DRIVE_CM_GROUP+1
DRIVE_DEGREES_GROUP = DRIVE_INCHES_GROUP+1
DRIVE_ROTATIONS_GROUP = DRIVE_DEGREES_GROUP+1
DRIVE_SECONDS_GROUP = DRIVE_ROTATIONS_GROUP+1
DRIVE_TURN = 12
DRIVE_TURN_LEFT = DRIVE_TURN+1
DRIVE_TURN_RIGHT = DRIVE_TURN_LEFT+1
DRIVE_TURN_AMOUNT = DRIVE_TURN_RIGHT+2
DRIVE_TURN_DEGREES = DRIVE_TURN_AMOUNT+2
DRIVE_TURN_ROTATIONS = DRIVE_TURN_DEGREES+1
DRIVE_TURN_SECONDS = DRIVE_TURN_ROTATIONS+1
STOP_GROUP = 23
EYES_GROUP = 24
EYES_OPEN_GROUP = EYES_GROUP+2
EYES_CLOSE_GROUP = EYES_GROUP+3
EYES_WHICH_GROUP = EYES_GROUP+4
EYES_BOTH_GROUP = EYES_GROUP+5
EYES_LEFT_GROUP = EYES_GROUP+6
EYES_RIGHT_GROUP = EYES_GROUP+7
EYE_COLOR_GROUP = 32
EYE_COLOR_LEFT_GROUP = EYE_COLOR_GROUP+2
EYE_COLOR_RIGHT_GROUP = EYE_COLOR_GROUP+3
EYE_COLOR_SETTING_GROUP = EYE_COLOR_GROUP+4
EYE_COLOR_R_GROUP = EYE_COLOR_GROUP+5
EYE_COLOR_G_GROUP = EYE_COLOR_GROUP+6
EYE_COLOR_B_GROUP = EYE_COLOR_GROUP+7
EYE_COLOR_HTML_GROUP = EYE_COLOR_GROUP+8
EYE_COLOR_STRING_GROUP = EYE_COLOR_GROUP+9
BLINKER_GROUP = 42
BLINKER_LEFT_GROUP = BLINKER_GROUP+2
BLINKER_RIGHT_GROUP = BLINKER_GROUP+3
BLINKER_SELECTION_GROUP = BLINKER_GROUP+4
BLINKER_STATUS_GROUP = BLINKER_GROUP+5
RESET_GROUP = 48
ENCODER_GROUP = 49
ENCODER_LEFT_GROUP = ENCODER_GROUP+3
ENCODER_RIGHT_GROUP = ENCODER_GROUP+4
ENCODER_LEFT2_GROUP = ENCODER_GROUP+6
ENCODER_RIGHT2_GROUP = ENCODER_GROUP+7
ENCODER_RESET_GROUP = ENCODER_GROUP+9
ENCODER_READ_GROUP = ENCODER_GROUP+9
ENCODER_VALUE_GROUP = ENCODER_GROUP+11



##################################################################
# HELPER FUNCTIONS
##################################################################

def set_regex_string():
    '''
    Sets up the regex string, and the test_msgs for asserting
    refer to https://regex101.com/ to make sense of it all

    regex explanation:
    1. Forward/Backward [x cm|inches|degrees|rotations|seconds
    2. [turn] Left/Right [x degrees]
    '''
    regex_seconds = "(s(?:e[c|g]?(?:[o|u]n(?:d)?)?(?:s)?)?)"
    regex_degrees = "(d(?:[e|a][c|g]+(?:re(?:e)?)?(?:s)?)?)"
    regex_right = "((?:w)?ri(?:[gh]*t(?:e)?))"
    regex_left = "(lef(?:t)?)"
    regex_rotations = "(rot(?:at(?:i)?on)?(?:s)?)"
    regex_inches = "(in(?:ches|ch)?)"
    
    # drive forward or backward
    # first group is direction
    # Must start with either F or B, 
    # be followed by either o (for forward) or a for backward
    # or be followed by w (for fwd, or bwd)
    # must end with a D
    # must only contain letters
    # second group is optional and is numeric only (may be float)
    # third group is unit 
    # supported units are cm, 
    #                     in, inches, i, 
    #                     deg, degree(s), d, 
    #                     rot, rotation(s), r,
    #                     s[econd],s[egund]
    # the unit is optional. If not there cm will be assumed
    regex_drive = "((F[o|w][A-Z]*D)|(B[a|w][a-z]*D))\s*(([0-9.]*)\s*((cm)|"+regex_inches+"|"+regex_degrees+"|"+regex_rotations+"|"+regex_seconds+")+)?"
    
    regex_stop = "(STOP)"
    
    regex_speed = "(SPE(?:E)?D)\s*[0-9.]+\s*(%)?"

    # second one:
    # (turn) left/right (x degrees/seconds)
    regex_turn = "(?:t(?:urn)?)?\s*("+regex_left+"|"+regex_right+")\s*(([0-9.]+)\s*("+regex_degrees+"|"+regex_rotations+"|"+regex_seconds+")?)*"
    
    # third one:
    # open/close left/right/both eye(s)
    regex_eyes = "(((open)|(close))\s*(("+regex_left+"|"+regex_right+"|both)?\s*eye[s]??))"
    
    regex_eyes_color = "(("+regex_left+"|"+regex_right+"|both)\s*eye[s]?\s*(([0-9]{1,3})(?:,|\s)+([0-9]{1,3})(?:,|\s)+([0-9]{1,3})|(#[0-9A-F]{6})|("+regex_accepted_colors+")))"

    # fourth one:
    # left/right/both blinker(s) on/off
    regex_blinkers = "(("+regex_left+"|"+regex_right+"|both)?\s*(blinker[s]?|LEDL|LEDR)\s*(on|255|off|0))"

    regex_reset = "(RESET)"
    
    regex_encoders = "((("+regex_left+"|"+regex_right+"|both)?encoder[s]?("+regex_left+"|"+regex_right+"|both)?)\s*((reset)|(read)|([0-9.]*)))"
    


    
    full_regex = ("^"+regex_drive + "$|" +
            regex_turn + "$|^" +
            regex_speed + "$|^" +
            regex_stop + "$|^" +
            regex_eyes + "$|^" +
            regex_eyes_color + "$|^" +
            regex_blinkers + "$|^" +
            regex_reset + "$|^" +
            regex_encoders +"$")

    # print (full_regex)
    return full_regex
    

SENSOR_DISTANCE_GROUP = 1
SENSOR_DISTANCE_PORT1 = SENSOR_DISTANCE_GROUP+2
SENSOR_DISTANCE_PORT2 = SENSOR_DISTANCE_GROUP+3
SENSOR_BUZZER_GROUP = 5
SENSOR_BUZZER_PORT1_GROUP = SENSOR_BUZZER_GROUP+2
SENSOR_BUZZER_PORT2_GROUP = SENSOR_BUZZER_GROUP+3
SENSOR_BUZZER_POWER_GROUP = SENSOR_BUZZER_GROUP+4
SENSOR_LED_GROUP = 10
SENSOR_LED_PORT1_GROUP = SENSOR_LED_GROUP+2
SENSOR_LED_PORT2_GROUP = SENSOR_LED_GROUP+3
SENSOR_LED_POWER_GROUP = SENSOR_LED_GROUP+4
SENSOR_LIGHT_GROUP = 15
SENSOR_LIGHT_PORT1_GROUP = SENSOR_LIGHT_GROUP+2
SENSOR_LIGHT_PORT2_GROUP = SENSOR_LIGHT_GROUP+3
SENSOR_LINE_GROUP = 19

def set_sensor_regex_string():
    regex_ADport = "(((?:AD|A|D)?1)|((?:AD|A|D)?2))"
    
    # group 1 distance
    # group 2 port (optional)
    regex_distance = "((?:get(?:_))?di(?:s)?t(?:ance)?\s*"+regex_ADport+"?)"
    regex_buzzer = "(BUZ(?:Z(?:E(?:R)?)?)?\s*"+regex_ADport+"\s*([0-9.]+|off|on))"
    regex_LED = "(LED\s*"+regex_ADport+"\s*([0-9.]+|off|on))"
    regex_light = "((?:light|lite|lit)\s*"+regex_ADport+"?)"
    regex_line = "(LINE)"    
    
    full_regex = ("^"+regex_distance + "$|^" +
                    regex_buzzer + "$|^" +
                    regex_LED + "$|^" +
                    regex_light + "$|^" +
                    regex_line +"$")

    # print (full_regex)
    return full_regex


def is_GoPiGo3_msg(msg):
    '''
    Is the msg supposed to be handled by GoPiGo3?
    Return: Boolean
        True if valid for GoPiGo3
        False otherwise
    '''
    return is_msg(compiled_regexGPG3,msg)


def is_GoPiGo3_Sensor_msg(msg):
    '''
    Check if msg is a valid Sensor command
    '''
    return is_msg(compiled_regexSensors,msg)


def is_msg(reg,msg):
    '''
    Check if msg is a valid form of the compiled regex
    '''
    retval = reg.match(msg.strip())

    if retval is None:
        return False
    else:
        print ("Recognized {}".format(msg))
        return True


def handle_GoPiGo3_msg(msg):
    '''
    parses the message
    dispatches to appropriate method
    '''
    if en_debug:
        print("received {}".format(msg.strip().lower()))
    
    sensors = {}

    regObj = compiled_regexGPG3.match(msg.strip().lower())
    if regObj is None:
        if en_debug:
            print ("GoPiGo3 command is not recognized")
        return None

    # for i in range(len(regObj.groups())+1):
    #     print ("{}: {}".format(i,regObj.group(i)))
        
    if regObj.group(DRIVE_GROUP):
        # print("go for a drive")

        sensors = drive_gpg(regObj)
        # Drive forward/Backward (for X Units)
    
    elif regObj.group(STOP_GROUP):
        # print('stop')
        sensors = gpg.stop()
    
    elif regObj.group(DRIVE_TURN):
        # print('turn')
        sensors = turn_gpg(regObj)
    
    elif regObj.group(EYES_GROUP):
        # print("eyes")
        sensors = handle_eyes(regObj)
        
    elif regObj.group(EYE_COLOR_GROUP):
        # print("eye color")
        sensors = handle_eye_color(regObj)
        
    elif regObj.group(BLINKER_GROUP):
        # print("blinkers")
        sensors = handle_blinkers(regObj)
        
    elif regObj.group(RESET_GROUP):
        sensors = GoPiGo3_reset();
        
    elif regObj.group(ENCODER_GROUP):
        # print("handling encoders")
        sensors = handle_encoders(regObj)
        
    return sensors


def handle_GoPiGo3_Sensor_msg(msg):
    if en_debug:
        print("received sensor {}".format(msg.strip().lower()))
        
    sensors = {}
    regObj = compiled_regexSensors.match(msg.strip().lower())
    if regObj is None:
        if en_debug:
            print ("GoPiGo3 Sensor command is not recognized")
        return None

    # for i in range(len(regObj.groups())+1):
    #     print ("{}: {}".format(i,regObj.group(i)))
    
    if regObj.group(SENSOR_DISTANCE_GROUP):
        sensors = handle_distance(regObj)
        
    elif regObj.group(SENSOR_BUZZER_GROUP):
        sensors = handle_buzzer(regObj)

    elif regObj.group(SENSOR_LED_GROUP):
        sensors = handle_led(regObj)

    elif regObj.group(SENSOR_LIGHT_GROUP):
        sensors = handle_light(regObj)

    elif regObj.group(SENSOR_LINE_GROUP):
        sensors = handle_line_sensor(regObj)
        
    return sensors

def handle_line_sensor(regObj):
    
    if en_debug:
        print ("line follower!")
        
    sensors = {}
    explanation = [
    "Completely to the right", 
    "Way to the right",
    "Going right",
    "Slightly to the right",
    "Center", 
    "Slightly to the left",
    "Going left",
    "Way to the left",
    "Completely to the left",
    "Reading black everywhere",
    "Reading white everywhere",
    "Technical difficulties"
    ]
    try:
        import sys
        # NOTE: for now te line follower is still kept in the GoPiGo folder
        sys.path.insert(0, '/home/pi/Dexter/GoPiGo/Software/Python/line_follower')
        # import line_sensor
        import scratch_line

    except ImportError:
        print ("Line sensor libraries not found")
        return({'line':-3,'line explanation': "technical difficulties"})

    try:
        line=scratch_line.line_sensor_val_scratch()
        if en_debug:
            print ("Line Sensor Readings: {}".format(str(line)))
        sensors["line"] = line
        sensors["line explanation"] = explanation[line+4]

    except Exception as e:
        if debug:
            print ("Error reading Line sensor: {}",format(str(e)))
        sensors["line"] = -3
    
    return sensors


def handle_light(regObj):
    sensors = {}
    light_reading = 0
    
    port = "AD2" if regObj.group(SENSOR_LIGHT_PORT2_GROUP) else "AD1"

    if known_sensors[port] == None or \
       isinstance(known_sensors[port], easy.LightSensor) is False:
        try:
            # print("Instancing Light Sensor")
            known_sensors[port] = easy.LightSensor(port,gpg)
            # time.sleep(0.01)
        except Exception as e:
            # print("handle_light {}".format(e))
            return ({"Light"+port:"technical difficulties"})
            
    # print("Reading from port {}".format(port))

    light_reading = known_sensors[port].percent_read()    
    sensors["{}: Light".format(port)] = light_reading
        
    return sensors
    
    
def handle_led(regObj):
    '''
    if a port is not provided assume AD1
    '''
    sensors = {}
    port = "AD2" if regObj.group(SENSOR_LED_PORT2_GROUP) else "AD1"
    
    if known_sensors[port] == None or \
       isinstance(known_sensors[port], easy.Led) is False:
        known_sensors[port] = easy.Led(port,gpg)
        
    try:
        power = float(regObj.group(SENSOR_LED_POWER_GROUP))
    except:
        power = 100 if regObj.group(SENSOR_LED_POWER_GROUP)=="on" else 0
        
    known_sensors[port].light_on(power)
    
    return {"{}: LED".format(port):power}


def handle_buzzer(regObj):
    '''
    if a port is not provided assume AD1
    '''
    sensors = {}
    port = "AD2" if regObj.group(SENSOR_BUZZER_PORT2_GROUP) else "AD1"
    
    if known_sensors[port] == None or \
       isinstance(known_sensors[port], easy.Buzzer) is False:
        known_sensors[port] = easy.Buzzer(port,gpg)
        
    try:
        power = float(regObj.group(SENSOR_BUZZER_POWER_GROUP))
    except:
        power = 100 if regObj.group(SENSOR_BUZZER_POWER_GROUP)=="on" else 0
        
    known_sensors[port].sound(power)
    
    return {"{}: Buzzer".format(port):power}


def handle_distance(regObj):
    '''
    if a port is provided, assume it's ultrasonic sensor
 
    If no port is provided :
        Try to deal with Distance Sensor first. 
        if Distance sensor fails, attempt US sensor on port AD1

    '''
    if regObj.group(SENSOR_DISTANCE_PORT2):
        port = "AD2" 
    elif regObj.group(SENSOR_DISTANCE_PORT1):
        port = "AD1" 
    else:
        port = None
  
    sensors = {}
    if port is None:
        if distance_sensor is not None:
            distance = distance_sensor.read()
            sensors["distance"] = distance
        
        # if no distance sensor, then default to port AD1
        else:
            # print("no port provided, going with AD1")
            port = "AD1"
    
    # don't use an else here even if it's tempting
    # as port can be modified in the first if block  
    if port:
        
        try:
            # create Ultrasonic sensor instance if needed
            if known_sensors[port] == None  or \
               isinstance(known_sensors[port], easy.UltraSonicSensor) is False:
                known_sensors[port] = easy.UltraSonicSensor(port,gpg)
        except Exception as e:
            # print ("handle_distance: {}".format(e))
                            
        # print("reading from ultrasonic sensor on port {}".format(port))
        distance = known_sensors[port].read()
        sensors["{}: distance".format(port)] = distance

    if en_debug:    
        print(sensors)
    return (sensors)
        
        
        
def handle_encoders(regObj):
    '''
    reset the encoders or go to a specific position
    '''
    sensors = {}
    # ask for an encode reset, either just one side, or both
    if regObj.group(ENCODER_RESET_GROUP):
        # print("encoder resetting")
        # if the right encoder wasn't specified, then it's either 
        # a left reset or both.
        if regObj.group(ENCODER_RIGHT_GROUP)==None and \
           regObj.group(ENCODER_RIGHT2_GROUP)==None:
            # print("resetting left encoder")
            gpg.set_motor_power(gpg.MOTOR_LEFT, 0)
            gpg.offset_motor_encoder(gpg.MOTOR_LEFT, 
                                    gpg.get_motor_encoder(gpg.MOTOR_LEFT))
            
        # if the left encoder wasn't specified, then it's either
        # the right or both
        if regObj.group(ENCODER_LEFT_GROUP)==None and \
           regObj.group(ENCODER_LEFT2_GROUP)==None:
            # print("resetting right encoder")
            gpg.set_motor_power(gpg.MOTOR_RIGHT, 0)
            gpg.offset_motor_encoder(gpg.MOTOR_RIGHT,
                                    gpg.get_motor_encoder(gpg.MOTOR_RIGHT))
    
    # ask for a specific position            
    if regObj.group(ENCODER_VALUE_GROUP):
        # if the right encoder wasn't specified, then it's either 
        # a left reset or both.
        if regObj.group(ENCODER_RIGHT_GROUP)==None and \
           regObj.group(ENCODER_RIGHT2_GROUP)==None:
                gpg.set_motor_position(gpg.MOTOR_LEFT, 
                                    int(regObj.group(ENCODER_VALUE_GROUP)))
        # if the left encoder wasn't specified, then it's either
        # the right or both
        if regObj.group(ENCODER_LEFT_GROUP)==None and \
           regObj.group(ENCODER_LEFT2_GROUP)==None:
                gpg.set_motor_position(gpg.MOTOR_RIGHT, 
                                        int(regObj.group(ENCODER_VALUE_GROUP)))

    # done for every code path, but most notable for ENCODER READ
    sensors["Encoder Left"] = gpg.get_motor_encoder(gpg.MOTOR_LEFT)
    sensors["Encoder Right"] = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
    return(sensors)


def GoPiGo3_reset():
    '''
    Resets the GoPiGo3
    '''
    gpg.reset_all()


def handle_blinkers(regObj):
    '''
    set left/right/both blinkers on/off
    '''
    # print("handle blinkers {}".format(regObj.group(BLINKER_STATUS_GROUP)))
    
    try:
        if regObj.group(BLINKER_SELECTION_GROUP) == "ledl":
            left = True
            right = False
        elif regObj.group(BLINKER_SELECTION_GROUP) == "ledr":
            right = True
            left = False
        else:
            left = True if regObj.group(BLINKER_RIGHT_GROUP) == None else False
            right = True if regObj.group(BLINKER_LEFT_GROUP) == None else False
        
        if regObj.group(BLINKER_STATUS_GROUP) == "on" or \
           regObj.group(BLINKER_STATUS_GROUP) == "255":
            if right:
                gpg.blinker_on("right")
            if left:
                gpg.blinker_on("left")   
        else:
            if right:
                gpg.blinker_off("right")
            if left:
                gpg.blinker_off("left") 
    except Exception as e:
        print("handle_blinkers: {}".format(e))    
    return None    


def handle_eye_color(regObj):
    '''
    set the color of one or both eyes, and open the eye
    '''
    if regObj.group(EYE_COLOR_STRING_GROUP):
        r,g,b=eye_colors[regObj.group(EYE_COLOR_STRING_GROUP)]

    if regObj.group(EYE_COLOR_R_GROUP):
        r = int(regObj.group(EYE_COLOR_R_GROUP))
    if regObj.group(EYE_COLOR_G_GROUP):
        g = int(regObj.group(EYE_COLOR_G_GROUP))
    if regObj.group(EYE_COLOR_B_GROUP):
        b = int(regObj.group(EYE_COLOR_B_GROUP))
    if regObj.group(EYE_COLOR_HTML_GROUP):
        color = regObj.group(EYE_COLOR_HTML_GROUP)
        r,g,b = tuple(int(color[i:i+2], 16) for i in (1, 3 ,5))
        
    try:
        if regObj.group(EYE_COLOR_LEFT_GROUP)==None:
            gpg.set_right_eye_color((r,g,b))
            gpg.open_right_eye()
        if regObj.group(EYE_COLOR_RIGHT_GROUP)==None:
            gpg.set_left_eye_color((r,g,b))
            gpg.open_left_eye()
    except Exception as e:
        print("handle_eye_color".format(e))
    
    return None


def handle_eyes(regObj):
    '''
    Open/Close left/right/both eyes
    '''
    if regObj.group(EYES_OPEN_GROUP):
        if regObj.group(EYES_RIGHT_GROUP)==None:
            gpg.open_left_eye()
        if regObj.group(EYES_LEFT_GROUP)==None:
            gpg.open_right_eye()
    if regObj.group(EYES_CLOSE_GROUP):
        if regObj.group(EYES_RIGHT_GROUP)==None:
            gpg.close_left_eye()
        if regObj.group(EYES_LEFT_GROUP)==None:
            gpg.close_right_eye()
    
    return None


def turn_gpg(regObj):
    '''
    Handles all turn movements
    Turn left/right
    Turn left/right X degrees/seconds/rotations
    '''
    
    # these will return encoder readings
    if regObj.group(DRIVE_TURN_AMOUNT):
        # print("turn x amount")
        try:
            turn_amount = int(regObj.group(DRIVE_TURN_AMOUNT))
        except Exception as e:
            print("turn_gpg: {}".format(e))
            pass
            
        if regObj.group(DRIVE_TURN_LEFT):
            turn_amount = turn_amount * -1
            
        if regObj.group(DRIVE_TURN_ROTATIONS):
            turn_amount = turn_amount * 360
            # print ( "gpg turn {} degrees".format(turn_amount))
            gpg.turn_degrees(turn_amount,blocking=True)
            
        elif regObj.group(DRIVE_TURN_SECONDS):
            if regObj.group(DRIVE_TURN_LEFT):
                # print("turning left")
                gpg.left()
            else:
                # print("turning right")
                gpg.right()
                
            # don't use turn_amount here as it could be negative when
            # going left
            time.sleep(float(regObj.group(DRIVE_TURN_AMOUNT)))
            gpg.stop()
            # print("stopped")

        # don't test for degrees per se as it's the default value
        # and is optional 
        # left 90 is the same as left 90 degrees
        else:
            # print ( "gpg turn {} degrees".format(turn_amount))
            try:
                gpg.turn_degrees(turn_amount,blocking=True)
            except Exception as e:
                print("turn_gpg: {}".format(e))
                pass     
                
        sensors["Encoder Left"] = gpg.get_motor_encoder(gpg.MOTOR_LEFT)
        sensors["Encoder Right"] = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
        return(sensors)

    # calls that will not require encoder readings
    if regObj.group(DRIVE_TURN_LEFT):
        # print("turn left")
        gpg.left()
        return None
    elif regObj.group(DRIVE_TURN_RIGHT):
        # print("turn right")
        gpg.right()
        return None


def drive_gpg(regObj):
    '''
    Handle driving forward or backward
    infinite, or X cm, or X inches, or X wheel rotations, or X seconds
    '''

    sensors = {}
    incoming_drive = regObj.group(DRIVE_GROUP)
    incoming_direction = ( 1 if regObj.group(DRIVE_DIRECTION_GROUP) != None else -1)
    incoming_distance = regObj.group(DRIVE_DISTANCE_GROUP)
    incoming_cm = regObj.group(DRIVE_CM_GROUP)
    incoming_inches = regObj.group(DRIVE_INCHES_GROUP)
    incoming_degrees = regObj.group(DRIVE_DEGREES_GROUP)
    incoming_rotations = regObj.group(DRIVE_ROTATIONS_GROUP)
    incoming_seconds = regObj.group(DRIVE_SECONDS_GROUP)

    
    # start with the calls that will not require encoder readings
    if incoming_distance == None:
        if incoming_direction > 0:
            # print("gpg forward")
            gpg.forward()
        else:
            # print("gpg backward")
            gpg.backward()
        return None

    # these will return encoder readings
    try:
        incoming_distance = float(incoming_distance)
    except:
        print("issue with casting distance to a float")
    if incoming_cm:
        # print ("gpg cm {}".format(incoming_distance*incoming_direction))
        gpg.drive_cm(incoming_distance*incoming_direction, blocking=True)
    elif incoming_inches:
        # print ("gpg inches {}".format(incoming_distance*incoming_direction))
        gpg.drive_inches(incoming_distance*incoming_direction, blocking=True)
    elif incoming_degrees:
        # print ("gpg degrees {}".format(incoming_distance*incoming_direction))
        gpg.drive_degrees(incoming_distance*incoming_direction, blocking=True)
    elif incoming_rotations: 
        # print ("gpg rotations {}".format(incoming_distance * incoming_direction))
        gpg.drive_degrees(incoming_distance*incoming_direction*360, blocking=True)
    elif incoming_seconds:
        # print("gpg forward")
        if incoming_direction > 0:
            gpg.forward()
        else:
            gpg.backward()
        time.sleep(incoming_distance)
        gpg.stop()
        # print ("gpg stopped")
        
    sensors["Encoder Left"] = gpg.get_motor_encoder(gpg.MOTOR_LEFT)
    sensors["Encoder Right"] = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
    return(sensors)

            
##################################################################
# MAIN FUNCTION
##################################################################
compiled_regexGPG3 = re.compile(set_regex_string(), re.IGNORECASE)
compiled_regexSensors = re.compile(set_sensor_regex_string(), re.IGNORECASE)

if __name__ == '__main__':
    
    print("Starting GoPiGo3 Scratch Controller")

    connected = 0   # This variable tells us if we're successfully connected.

    while(connected == 0):
        startTime = time.time()
        try:
            s = scratch.Scratch()
            if s.connected:
                if en_debug:
                    print("GoPiGo3 Scratch: Connected to Scratch successfully")
            connected = 1   # We are succesfully connected!  Exit Away!

        except scratch.ScratchError:
            arbitrary_delay = 10  # no need to issue error statement if at least 10 seconds haven't gone by.
            if (time.time() - startTime > arbitrary_delay):
                print ("GoPiGo3 Scratch: Scratch is either not opened or remote sensor connections aren't enabled")

    try:
        s.broadcast('READY')
        s.broadcast("forward")
        s.broadcast("backward")
        s.broadcast("turn left")
        s.broadcast("turn right")
        s.broadcast("stop")
        s.broadcast("open eyes")
        s.broadcast("close eyes")
        s.broadcast("blinkers on")
        s.broadcast("blinkers off")
        sensors["Encoder Left"] = gpg.get_motor_encoder(gpg.MOTOR_LEFT)
        sensors["Encoder Right"] = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
        s.sensorupdate(sensors)

    except NameError:
        if en_debug:
            print ("GoPiGo3 Scratch: Unable to Broadcast")

    while True:
        try:
            m = s.receive()

            while m is None or m[0] == 'sensor-update' :
                m = s.receive()

            msg = m[1]

# remove all spaces in the input msg to create ms_nospace
# gopigo3 handles the one without spaces but we keep the one with spaces
# for others (like pivotpi, camera, line_sensor) as a precautionary measure.
            try:
                msg_nospace = msg.replace(" ","")
            except:
                pass


            if en_debug:
                print("Rx:{}".format(msg))

            if is_GoPiGo3_msg(msg_nospace):
                sensors = handle_GoPiGo3_msg(msg_nospace)
                if sensors is not None:
                    s.sensorupdate(sensors)
                    
            elif is_GoPiGo3_Sensor_msg(msg_nospace):
                sensors = handle_GoPiGo3_Sensor_msg(msg_nospace)
                if sensors is not None:
                    s.sensorupdate(sensors)

            # CREATE FOLDER TO SAVE PHOTOS IN

            elif msg[:6].lower()=="FOLDER".lower():
                print ("Camera folder")
                try:
                    cameraFolder=defaultCameraFolder+str(msg[6:]).strip()
                    print(cameraFolder)
                    if not os.path.exists(cameraFolder):
                        pi=1000  # uid and gid of user pi
                        os.makedirs(cameraFolder)
                        os.chown(cameraFolder,pi,pi)
                        s.sensorupdate({"folder":"created"})
                    else:
                        s.sensorupdate({"folder":"set"})
                except:
                    print ("error with folder name")

            # TAKE A PICTURE

            elif msg.lower()=="TAKE_PICTURE".lower():
                print ("TAKE_PICTURE" )
                pi=1000  # uid and gid of user pi
                try:
                    from subprocess import call
                    import datetime
                    newimage = "{}/img_{}.jpg".format(cameraFolder,str(datetime.datetime.now()).replace(" ","_",10))
                    photo_cmd="raspistill -o {} -w 640 -h 480 -t 1".format(newimage)
                    call ([photo_cmd], shell=True)
                    os.chown(newimage,pi,pi)
                    if en_debug:
                        print ("Picture Taken")
                    s.sensorupdate({'camera':"Picture Taken"})
                except:
                    if en_debug:
                        e = sys.exc_info()[1]
                        print ("Error taking picture")
                    s.sensorupdate({'camera':"Error"})


            elif (msg[:5].lower()=="SPEAK".lower()):
                try:
                    from subprocess import call
                    cmd_beg = "espeak -ven+f1 "
                    in_text = msg[len("SPEAK"):]
                    cmd_end = " 2>/dev/null"
                    out_str = cmd_beg+"\""+in_text+"\""+cmd_end
                    if en_debug:
                        print(out_str)
                    call([out_str], shell=True)

                except:
                    print("Issue with espeak")

            # PIVOTPI
            elif pivotpi_available==True and PivotPiScratch.isPivotPiMsg(msg):
                pivotsensors = PivotPiScratch.handlePivotPi(msg)
                # print "Back from PivotPi",pivotsensors
                s.sensorupdate(pivotsensors)

            else:
                if en_debug:
                    print ("Ignoring Command: {}".format(msg))

        except KeyboardInterrupt:
            running = False
            if en_debug:
                print("GoPiGo3 Scratch: Disconnected from Scratch")
            break
        except (scratch.scratch.ScratchConnectionError, NameError) as e:
            print("exception error: ", e)
            while True:
                # thread1.join(0)
                if en_debug:
                    print("GoPiGo3 Scratch: Scratch connection error, Retrying")
                time.sleep(5)
                try:
                    s = scratch.Scratch()
                    s.broadcast('READY')
                    if en_debug:
                        print("GoPiGo3 Scratch: Connected to Scratch successfully")
                    break
                except scratch.ScratchError:
                    if en_debug:
                        print("GoPiGo3 Scratch: Scratch is either not opened or remote sensor connections aren't enabled\n..............................\n")
        except Exception as e:
            if en_debug:
                print("GoPiGo3 Scratch: Error %s" % e)
