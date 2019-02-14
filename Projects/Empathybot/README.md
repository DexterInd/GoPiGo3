# Empathybot: The Raspberry Pi Robot That Reads Human Emotion

![ GoPiGo ](https://github.com/DexterInd/GoPiGo/raw/master/Projects/Empathybot/Empathybot.jpg)

In this project we built emotional intelligence to our robot.  We developed a Raspberry Pi Robot with the GoPiGo that will drive up to you, read your emotions, and then try to have a conversation with you, based on how you’re feeling.  We will show you how you too can build your own DIY emotion-reading robot with a Raspberry Pi.

![ GoPiGo ](https://github.com/DexterInd/GoPiGo/raw/master/Projects/Empathybot/Emotions.jpg)

# Details

In this tutorial, we build a robot that responds to human emtions.  We developed a Raspberry Pi Robot with the GoPiGo that will drive up to you, read your emotions, and then try to have a conversation with you, based on how you’re feeling.  We will show you how you too can build your own DIY emotion-reading robot with a Raspberry Pi.
See the detailed tutorial here:  http://www.dexterindustries.com/projects/empathybot-raspberry-pi-robot-with-emotional-intelligence/
This project uses Google Cloud Vision on the Raspberry Pi to take a picture with the Raspberry Pi Camera and analyze human emotions with the Google Cloud Vision API.

Google Vision API Tutorial with a Raspberry Pi and Raspberry Pi Camera.  See more about it here:  https://www.dexterindustries.com/howto/use-google-cloud-vision-on-the-raspberry-pi/

Some Preparation:
```
sudo apt-get update
sudo apt-get install espeak
sudo pip install --upgrade google-auth
```

The Following Commands are Useful!
```
sudo su
export GOOGLE_APPLICATION_CREDENTIALS=vision1-your_file_Name_here.json
python empathybot.py &
```

If you receive an error from Google about your certificates lifespan, try setting the Raspberry Pi time and date manually (in UTC time): `date -u 110720262016`

Helpful Picamera Notes: https://www.raspberrypi.org/documentation/usage/camera/python/README.md

Relevant JSON Responses from Google:
```json
{
    "sorrowLikelihood": "VERY_UNLIKELY",
    "surpriseLikelihood": "VERY_UNLIKELY",
    "angerLikelihood": "VERY_UNLIKELY",
    "blurredLikelihood": "VERY_UNLIKELY",
    "joyLikelihood": "POSSIBLE"
}
```

# See Also

The GoPiGo is a delightful and complete robot for the Raspberry Pi that turns your Pi into a fully operating robot.  GoPiGo is a mobile robotic platform for the Raspberry Pi developed by [Dexter Industries.](http://www.dexterindustries.com/GoPiGo)  

- [Dexter Industries] (http://www.dexterindustries.com/GoPiGo)
- [Kickstarter Campaign] (http://kck.st/Q6vVOP)
- [Raspberry Pi] (http://www.raspberrypi.org/)