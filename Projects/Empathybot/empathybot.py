#! /usr/local/bin/python

distance_from_body = 50	# Distance the GoPiGo will stop from the human body.
gopigo_speed = 150		# Power of the motors.  Increase or decrease depending on how fast you want to go.

import argparse
import urllib2
import base64
import picamera
import json
from subprocess import call
import time
import datetime
import atexit
from googleapiclient import discovery
import google.auth
from easygopigo3 import EasyGoPiGo3
from di_sensors.easy_distance_sensor import EasyDistanceSensor

gpg = EasyGoPiGo3()
button = gpg.init_button_sensor("AD1") # button on GoPiGo3's AD1 port
ds = EasyDistanceSensor() # distance sensor on I2C port

atexit.register(gpg.stop)	# If we exit, stop the motors

#Calls the Espeak TTS Engine to read aloud a sentence
# This function is going to read aloud some text over the speakers
def sound(spk):
	#	-ven+m7:	Male voice
	#  The variants are +m1 +m2 +m3 +m4 +m5 +m6 +m7 for male voices and +f1 +f2 +f3 +f4 which simulate female voices by using higher pitches. Other variants include +croak and +whisper.
	#  Run the command espeak --voices for a list of voices.
	#	-s180:		set reading to 180 Words per minute
	#	-k20:		Emphasis on Capital letters

	# to enable audio output on the audio jack
	# otherwise, instead of one, select 2 for HDMI or 0 for automatic
	call("amixer cset numid=3 1", shell=True)
	call("amixer set PCM 100", shell=True) # Crank up the volume!

	cmd_beg=" espeak -ven-us+f3 -a 200 -s145 -k20 --stdout '"
	cmd_end="' | aplay"
	print(cmd_beg+spk+cmd_end)
	call([cmd_beg+spk+cmd_end], shell=True)

def takephoto():
    date_string = str(datetime.datetime.now())
    camera = picamera.PiCamera()
    camera.resolution = (1600, 1200)
    camera.sharpness = 100
    date_string = 'image'+date_string+'.jpg'
    date_string = date_string.replace(":", "")	# Strip out the colon from date time.
    date_string = date_string.replace(" ", "")	# Strip out the space from date time.
    print("TAKE PICTURE: " + date_string)
    print(date_string)
    camera.capture('image.jpg')
    camera.close()	# We need to close off the resources or we'll get an error.
    call(["cp /home/pi/image.jpg " + "/home/pi/"+date_string], shell=True)

def parse_response(json_response):
	# print json_response
	try:
		# print json.dumps(response, indent=4, sort_keys=True)	#Print it out and make it somewhat pretty.
		anger = json_response['responses'][0]['faceAnnotations'][0]['angerLikelihood']
		surprise = json_response['responses'][0]['faceAnnotations'][0]['surpriseLikelihood']
		sorrow = json_response['responses'][0]['faceAnnotations'][0]['sorrowLikelihood']
		blurr = json_response['responses'][0]['faceAnnotations'][0]['blurredLikelihood']
		joy = json_response['responses'][0]['faceAnnotations'][0]['joyLikelihood']
		
		anger_string = (str(anger))
		surprise_string = (str(surprise))
		sorrow_string = (str(sorrow))
		# print(str(blurr))
		happy_string = (str(joy))
		
		print("Happy: " + happy_string)
		print("Angry: " + anger_string)
		print("Surprise: " + surprise_string)
		print("Sorrow: " + sorrow_string)
		# sound("You look pretty. . . . tired.  You must have an infant?")
		
		if(happy_string != "VERY_UNLIKELY"):
			sound("You seem happy!  Tell me why you are so happy!")
		elif(anger_string != "VERY_UNLIKELY"):
			sound("Uh oh, you seem angry!  I have kids, please don't hurt me!")
		elif(surprise_string != "VERY_UNLIKELY"):
			sound("You seem surprised!  ")
		else:
			sound("You seem sad!  Would you like a hug?")
		
	except:
		sound("I am sorry, I can not see your face.  May I try again?")
	
def take_emotion():
	takephoto() # First take a picture
	"""Run a label request on a single image"""

	credentials, project_id = google.auth.default()
	print(credentials)
	service = discovery.build('vision', 'v1', credentials=credentials)

	with open('image.jpg', 'rb') as image:
		image_content = base64.b64encode(image.read())
		service_request = service.images().annotate(body={
			'requests': [{
			'image': {
			'content': image_content.decode('UTF-8')
			},
			'features': [{
			'type': 'FACE_DETECTION',
			'maxResults': 10
			}]
			}]
		})
		response = service_request.execute()
		parse_response(response)

# Wait for Button Press.
def wait_for_button():
	gpg.stop()
	while button.is_button_pressed() is False:
		time.sleep(0.5)
	print("Button pressed!")
	
	gpg.forward()
	while ds.read() > distance_from_body:
		time.sleep(0.1)
	gpg.stop()
	
	sound("Hello!")

def back_away():
	gpg.drive_cm(-50)
	
def internet_on():
	try:
		urllib2.urlopen('https://google.com', timeout=1)
		return True
	except urllib2.URLError as err: 
		return False
		
def main():

	sound("Hello!  I  am  empathy  bot!")  

	while (internet_on() != True):
		sound("I am waiting on an internet connection!")
		time.sleep(15)

	sound("I am ready to empathize!")  
	while True:
		# Wait for button press.
		wait_for_button()
		take_emotion()
		back_away()

if __name__ == '__main__':
    main()
