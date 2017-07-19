# import the time library for the sleep function
import time

# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
gpg = easy.EasyGoPiGo3()

# Create an instance of the Buzzer
# connect a buzzer to port AD2
my_buzzer = gpg.init_buzzer("AD2")

twinkle = ["C4","C4","G4","G4","A4","A4","G4"]

print("Expecting a buzzer on Port AD2")
print("A4")
buzzer.sound(440)
time.sleep(1)
print("A5")
buzzer.sound(880)
time.sleep(1)
print("A3")
buzzer.sound(220)
time.sleep(1)

for note in twinkle:
    print(note)
    my_buzzer.sound(buzzer.scale[note])
    time.sleep(0.5)
    buzzer.sound_off()
    time.sleep(0.25)

buzzer.sound_off()
