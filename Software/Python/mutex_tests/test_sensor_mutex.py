#################################################
'''
This file checks that the mutex value trickles down
to each sensor, when the init methods are called
from easygopigo3
'''
#################################################


import easygopigo3 as easy

gpg3 = easy.EasyGoPiGo3(use_mutex=True)
print(gpg3.use_mutex)

init_calls = [
    gpg3.init_light_sensor,
    gpg3.init_sound_sensor,
    gpg3.init_loudness_sensor,
    gpg3.init_ultrasonic_sensor,  
    gpg3.init_buzzer,
    gpg3.init_led,
    gpg3.init_button_sensor,
    gpg3.init_line_follower,
    gpg3.init_servo,
    gpg3.init_distance_sensor,
    gpg3.init_dht_sensor,
    gpg3.init_remote,
    gpg3.init_motion_sensor
]

count = 0
for init_call in init_calls:
    count += 1
    
    # line follower raises an error if not connected
    try:
        sensor = init_call()
    except:
        sensor = None
    if sensor != None:
        print(count, sensor.use_mutex)
        assert(sensor.use_mutex == gpg3.use_mutex)
    else:
        print("skipped {}".format(count))