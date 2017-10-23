import time
import easygopigo3 as easy
gpg = easy.EasyGoPiGo3(use_mutex=True)

my_Distance_portI2C = easy.DistanceSensor('I2C', gpg, use_mutex=True)
time.sleep(0.1)


# start()
while True:
        dist =  my_Distance_portI2C.read_mm()
	print(dist)
        if dist == 0:
		exit()
        else:
		print(".")
        time.sleep(0.1)

