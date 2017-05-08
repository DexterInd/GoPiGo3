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
print("A4")
my_buzzer.sound(440)
time.sleep(1)
print("A5")
my_buzzer.sound(880)
time.sleep(1)
print("A3")
my_buzzer.sound(220)
time.sleep(1)
my_buzzer.sound_off()
