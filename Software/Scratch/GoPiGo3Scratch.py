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
    print ("Scratch Interpreted closed")


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
    print ("Scratch Interpreted closed: {}".format(error.args[0]))
    sys.exit()
except IOError as error:
    error_box("Connection Error: {}".format(error.args[0]))
    print(error.args[0], ". Exiting...")
    sys.exit()
except Exception as e:
    error_box("Unknown Error, closing Scratch Interpreter")
    print("Unknown Error: {}".format(e))


defaultCameraFolder="/home/pi/Desktop/"
cameraFolder = defaultCameraFolder

##################################################################
# HELPER FUNCTIONS
##################################################################

def get_regex_sensors():
    '''
    generate a regex ready string with all the sensor_types keys
    '''
    list_of_sensors = ""

    return list_of_sensors


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

def set_regex_string():
    '''
    Sets up the regex string, and the test_msgs for asserting

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
    regex_turn = "(?:t(?:urn)?)?\s*("+regex_left+"|"+regex_right+")\s*(([0-9.]+)\s*("+regex_degrees+"|"+regex_rotations+"|"+regex_seconds+")*)*"
    
    # third one:
    # open/close left/right/both eye(s)
    regex_eyes = "(((open)|(close))\s*(("+regex_left+"|"+regex_right+"|both)?\s*eye[s]??))"
    
    regex_eyes_color = "(("+regex_left+"|"+regex_right+"|both)\s*eye[s]*\s*(([0-9]{1,3})(?:,|\s)+([0-9]{1,3})(?:,|\s)+([0-9]{1,3})|(#[0-9A-F]{6})|("+regex_accepted_colors+")))"

    # fourth one:
    # left/right/both blinker(s) on/off
    regex_blinkers = "("+regex_left+"|"+regex_right+"|both)\s*(blinker[s]*)\s*(on|off)"
    
    full_regex = ("^"+regex_drive + "$|" +
            regex_turn + "$|^" +
            regex_speed + "$|^" +
            regex_stop + "$|^" +
            regex_eyes + "$|^" +
            regex_eyes_color + "$|^" +
            regex_blinkers)

    print (full_regex)
    return full_regex


def is_GoPiGo3_msg(msg):
    '''
    Is the msg supposed to be handled by GoPiGo3?
    Return: Boolean
        True if valid for GoPiGo3
        False otherwise
    '''
    retval = compiled_regexGPG3.match(msg.strip())

    if retval is None:
        return False
    else:
        print ("Recognized {}".format(msg))
        return True


def GoPiGo3_reset():
    '''
    Resets the GoPiGo3
    '''
    gpg.reset_all()


def handle_GoPiGo3_msg(msg):
    '''
    parses the message
    dispatches to appropriate method
    '''
    if en_debug:
        print("received {}".format(msg.strip().lower()))

    regObj = compiled_regexGPG3.match(msg.strip().lower())
    if regObj is None:
        if en_debug:
            print ("GoPiGo3 command is not recognized")
        return None

    for i in range(len(regObj.groups())):
        print ("{}: {}".format(i,regObj.group(i)))
        
    if regObj.group(DRIVE_GROUP):
        print("go for a drive")
        drive_gpg(regObj)
        # Drive forward/Backward (for X Units)
    
    elif regObj.group(STOP_GROUP):
        print('stop')
        gpg.stop()
    
    elif regObj.group(DRIVE_TURN):
        print('turn')
        turn_gpg(regObj)
    
    elif regObj.group(EYES_GROUP):
        print("eyes")
        handle_eyes(regObj)
        
    elif regObj.groups(EYE_COLOR_GROUP):
        print("eye color")
        handle_eye_color(regObj)
        

def handle_eye_color(regObj):
    '''
    set the color of one or both eyes, and open the eye
    '''
    if regObj.group(EYE_COLOR_STRING_GROUP):
        print("got a string")
        r,g,b=eye_colors[regObj.group(EYE_COLOR_STRING_GROUP)]

    if regObj.group(EYE_COLOR_R_GROUP):
        r = int(regObj.group(EYE_COLOR_R_GROUP))
    if regObj.group(EYE_COLOR_G_GROUP):
        g = int(regObj.group(EYE_COLOR_G_GROUP))
    if regObj.group(EYE_COLOR_B_GROUP):
        b = int(regObj.group(EYE_COLOR_B_GROUP))
    if regObj.group(EYE_COLOR_HTML_GROUP):
        color = regObj.group(EYE_COLOR_HTML_GROUP)
        print(color)
        r,g,b = tuple(int(color[i:i+2], 16) for i in (1, 3 ,5))
        
    print(r,g,b)
    
    try:
        if regObj.group(EYE_COLOR_LEFT_GROUP)==None:
            gpg.set_right_eye_color((r,g,b))
            gpg.open_right_eye()
        if regObj.group(EYE_COLOR_RIGHT_GROUP)==None:
            gpg.set_left_eye_color((r,g,b))
            gpg.open_left_eye()
    except Exception as e:
        print("handle_eye_color".format(e))


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

def turn_gpg(regObj):
    '''
    Handles all turn movements
    Turn left/right
    Turn left/right X degrees/seconds/rotations
    '''
    print ("turn_gpg")
    if regObj.group(DRIVE_TURN_AMOUNT):
        print("turn x amount")
        try:
            turn_amount = float(regObj.group(DRIVE_TURN_AMOUNT))
        except:
            pass
        if regObj.group(DRIVE_TURN_LEFT):
            turn_amount = turn_amount * -1
        if regObj.group(DRIVE_TURN_ROTATIONS):
            turn_amount = turn_amount * 360
            print ( "gpg turn {} degrees".format(turn_amount))
            gpg.turn_degrees(turn_amount)
        if regObj.group(DRIVE_TURN_DEGREES):
            print ( "gpg turn {} degrees".format(turn_amount))
            gpg.turn_degrees(turn_amount)
        if regObj.group(DRIVE_TURN_SECONDS):
            if regObj.group(DRIVE_TURN_LEFT):
                print("turning left")
                gpg.left()
            else:
                print("turning right")
                gpg.right()
                
            # don't use turn_amount here as it could be negative when
            # going left
            time.sleep(float(regObj.group(DRIVE_TURN_AMOUNT)))
            gpg.stop()
            print("stopped")

    elif regObj.group(DRIVE_TURN_LEFT):
        print("turn left")
        gpg.left()
    elif regObj.group(DRIVE_TURN_RIGHT):
        print("turn right")
        gpg.right()
    else:
        print("turn error")

    
def drive_gpg(regObj):
    '''
    Handle driving forward or backward
    infinite, or X cm, or X inches, or X wheel rotations, or X seconds
    '''
    incoming_drive = regObj.group(DRIVE_GROUP)
    incoming_direction = ( 1 if regObj.group(DRIVE_DIRECTION_GROUP) != None else -1)
    incoming_distance = regObj.group(DRIVE_DISTANCE_GROUP)
    incoming_cm = regObj.group(DRIVE_CM_GROUP)
    incoming_inches = regObj.group(DRIVE_INCHES_GROUP)
    incoming_degrees = regObj.group(DRIVE_DEGREES_GROUP)
    incoming_rotations = regObj.group(DRIVE_ROTATIONS_GROUP)
    incoming_seconds = regObj.group(DRIVE_SECONDS_GROUP)
    print ("{} {} {} {} {} {} {} {}".format(incoming_drive,incoming_direction, incoming_distance,incoming_cm,incoming_inches,incoming_degrees,incoming_rotations,incoming_seconds))
    
    if incoming_distance == None:
        if incoming_direction > 0:
            print("gpg forward")
            gpg.forward()
        else:
            print("gpg backward")
            gpg.backward()
    else:
        try:
            incoming_distance = float(incoming_distance)
        except:
            print("issue with casting distance to a float")
        if incoming_cm:
            print ("gpg cm {}".format(incoming_distance*incoming_direction))
            gpg.drive_cm(incoming_distance*incoming_direction)
        elif incoming_inches:
            print ("gpg inches {}".format(incoming_distance*incoming_direction))
            gpg.drive_inches(incoming_distance*incoming_direction)
        elif incoming_degrees:
            print ("gpg degrees {}".format(incoming_distance*incoming_direction))
            gpg.drive_degrees(incoming_distance*incoming_direction)
        elif incoming_rotations: 
            print ("gpg rotations {}".format(incoming_distance*incoming_direction))
            gpg.drive_degrees(incoming_distance*incoming_direction*360)
        elif incoming_seconds:
            print("gpg forward")
            if incoming_direction > 0:
                gpg.forward()
            else:
                gpg.backward()
            time.sleep(incoming_distance)
            gpg.stop()
            print ("gpg stopped")
            
##################################################################
# MAIN FUNCTION
##################################################################
compiled_regexGPG3 = re.compile(set_regex_string(), re.IGNORECASE)

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
            # time.sleep(1)

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
    except NameError:
        if en_debug:
            print ("GoPiGo3 Scratch: Unable to Broadcast")

    while True:
        try:
            m = s.receive()

            while m is None or m[0] == 'sensor-update' :

                # keep this for reference.
                # may work to detect File/new, File/Open but needs a change in scratchpi
                # to detect "send_vars" msg as being valid
                # if m[0] == "send_vars":  # File/New
                #     print("Resetting everything")
                #     SensorType = ["None","None","None","None"]
                #     for port in range(4):
                #         BP3.set_sensor_type(bp3ports[port], sensor_types["NONE"][0])

                m = s.receive()

            msg = m[1]

# remove all spaces in the input msg to create ms_nospace
# brickpi3 handles the one without spaces but we keep the one with spaces
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

            # Get the value from the Dexter Industries line sensor
            elif msg.lower()=="LINE".lower():
                try:
                    import sys

                    # NOTE: for now te line follower is still kept in the GoPiGo folder
                    sys.path.insert(0, '/home/pi/Dexter/GoPiGo/Software/Python/line_follower')
                    # import line_sensor
                    import scratch_line

                except ImportError:
                    print ("Line sensor libraries not found")
                    s.sensorupdate({'line':-3})

                if en_debug:
                    print ("LINE!")

                try:
                    line=scratch_line.line_sensor_val_scratch()
                    if en_debug:
                        print ("Line Sensor Readings: ".format(str(line)))
                    s.sensorupdate({'line':line})

                except:
                    if en_debug:
                        e = sys.exc_info()[1]
                        print ("Error reading Line sensor: ",format(str(e)))

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
        except:
            e = sys.exc_info()[0]
            if en_debug:
                print("GoPiGo3 Scratch: Error %s" % e)
