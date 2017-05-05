# import the EasyGoPiGo3 drivers
import easygopigo3 as easy
import time

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
GPG = easy.EasyGoPiGo3()


# create the LED instance, passing the port and GPG
my_LED = easy.Led("AD1",GPG)
# or
# my_LED = easy.Led("AD2")

# loop 100 times
for i in range(100):
    my_LED.light_max() # turn LED at max power
    time.sleep(0.5)
    my_LED.light_on(30)  # 30% power
    time.sleep(0.5)
    my_LED.light_off() # turn LED off
    time.sleep(0.5)

