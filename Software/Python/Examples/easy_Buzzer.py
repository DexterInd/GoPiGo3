# import the time library for the sleep function
import time

# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
GPG = easy.EasyGoPiGo3()

# Create an instance of the Buzzer
my_buzzer = easy.Buzzer("AD1", GPG)

my_buzzer.sound_on()
time.sleep(1)
my_buzzer.sound_off()
