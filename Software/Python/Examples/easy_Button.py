# import the time library for the sleep function
import time

# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
gpg = easy.EasyGoPiGo3()

# Put a grove button in port AD1
my_button = gpg.init_button_sensor("AD1")

print("Ensure there's a button in port AD1")
print("Press and release the button as often as you want")
print("the program will run for 2 minutes or")
print("Ctrl-C to interrupt it")


start = time.time()
RELEASED = 0
PRESSED = 1
state = RELEASED

while time.time() - start < 120:

    if state == RELEASED and my_button.read() == 1:
        print("PRESSED")
        gpg.open_eyes()
        state = PRESSED
    if state == PRESSED and my_button.read() == 0:
        print("RELEASED")
        gpg.close_eyes()
        state = RELEASED
    time.sleep(0.05)

print("All done!")
