# import the time library for the sleep function
import time

# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
GPG = easy.EasyGoPiGo3()

# Create an instance of the Buzzer
# connect a buzzer to port AD2
my_buzzer = easy.Buzzer("AD2", GPG)

print("Expecting a buzzer on Port AD2")
my_buzzer.sound_on()
time.sleep(1)
print("at 80")
my_buzzer.sound(80)
time.sleep(1)
print("at 50")
my_buzzer.sound(50)
time.sleep(1)
print("at 30")
my_buzzer.sound(30)
time.sleep(1)
my_buzzer.sound_off()
