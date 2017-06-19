"""
The purpose of this file is mostly to check the regex in GoPiGo3Scratch
Creation: Nicole Parrot - June 14th 2017
"""


import GoPiGo3Scratch as s


def test_sensors():
    
    # Distance Sensor and Ultrasonic Sensor
    assert(s.is_GoPiGo3_Sensor_msg("distance AD1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("get_distance AD1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("dist AD1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("distance AD2")==True)
    assert(s.is_GoPiGo3_Sensor_msg("get_distance AD2")==True)
    assert(s.is_GoPiGo3_Sensor_msg("dist AD2")==True)
    assert(s.is_GoPiGo3_Sensor_msg("distance")==True)
    assert(s.is_GoPiGo3_Sensor_msg("get_distance")==True)
    assert(s.is_GoPiGo3_Sensor_msg("dist")==True)
    assert(s.is_GoPiGo3_Sensor_msg("get_dist")==True)

    
    # Buzzer
    assert(s.is_GoPiGo3_Sensor_msg("buzzer")==False)
    assert(s.is_GoPiGo3_Sensor_msg("buzzer ad1 200")==True)
    assert(s.is_GoPiGo3_Sensor_msg("buzzer ad2 300")==True)
    assert(s.is_GoPiGo3_Sensor_msg("buzzer d2 300")==True)
    assert(s.is_GoPiGo3_Sensor_msg("buzz 2 300")==True)
    assert(s.is_GoPiGo3_Sensor_msg("buzz 300")==False)
    
    # Led
    assert(s.is_GoPiGo3_Sensor_msg("led")==False)
    assert(s.is_GoPiGo3_Sensor_msg("led ad1 200")==True)
    assert(s.is_GoPiGo3_Sensor_msg("led ad2 300")==True)
    assert(s.is_GoPiGo3_Sensor_msg("led d1 300")==True)
    assert(s.is_GoPiGo3_Sensor_msg("led 2 300")==True)
    assert(s.is_GoPiGo3_Sensor_msg("led 300")==False)
    
    # Light
    assert(s.is_GoPiGo3_Sensor_msg("light AD1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("light AD2")==True)
    assert(s.is_GoPiGo3_Sensor_msg("lite AD1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("light D1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("lit D2")==True)
    
    #Line follower
    assert(s.is_GoPiGo3_Sensor_msg("line")==True) 
    
    # SERVO 
    assert(s.is_GoPiGo3_Sensor_msg("servo1 120")==True) 
    assert(s.is_GoPiGo3_Sensor_msg("servo 1 120")==True)
    assert(s.is_GoPiGo3_Sensor_msg("servo2 20")==True) 
    assert(s.is_GoPiGo3_Sensor_msg("servo 2 20")==True)  
    assert(s.is_GoPiGo3_Sensor_msg("servo  2 20")==True)
    assert(s.is_GoPiGo3_Sensor_msg("servo  2 2 0")==False) 
    assert(s.is_GoPiGo3_Sensor_msg("servo2  220")==False) 
    
    # BUTTON
    assert(s.is_GoPiGo3_Sensor_msg("button AD1")==True)
    assert(s.is_GoPiGo3_Sensor_msg("BUTT AD2")==False)
    
if __name__ == '__main__':
    test_sensors()
