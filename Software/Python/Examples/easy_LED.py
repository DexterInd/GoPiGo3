# import the EasyGoPiGo3 drivers
import time
import easygopigo3 as easy

# This example will turn a Grove LED on the GoPiGo3 AD1 port on and off.

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
gpg = easy.EasyGoPiGo3()


# create the LED instance, passing the port and GPG
my_led = gpg.init_led("AD1")
# or
# my_LED = easy.Led("AD1", GPG)

# loop 100 times
for i in range(100):
    my_led.light_max() # turn LED at max power
    time.sleep(0.5)

    my_led.light_on(30)  # 30% power
    time.sleep(0.5)

    my_led.light_off() # turn LED off
    time.sleep(0.5)
