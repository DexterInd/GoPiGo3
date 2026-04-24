# GoPiGo3 Python package
from .gopigo3 import GoPiGo3, FirmwareVersionError, GoPiGoValueError
from .easygopigo3 import EasyGoPiGo3
from .easysensors import (
    Sensor,
    DigitalSensor,
    AnalogSensor,
    LightSensor,
    SoundSensor,
    LoudnessSensor,
    UltraSonicSensor,
    Buzzer,
    Led,
    MotionSensor,
    ButtonSensor,
    Remote,
    Servo,
    DHTSensor,
)

__version__ = "1.0.01"
__all__ = [
    "GoPiGo3",
    "FirmwareVersionError",
    "GoPiGoValueError",
    "EasyGoPiGo3",
    "Sensor",
    "DigitalSensor",
    "AnalogSensor",
    "LightSensor",
    "SoundSensor",
    "LoudnessSensor",
    "UltraSonicSensor",
    "Buzzer",
    "Led",
    "MotionSensor",
    "ButtonSensor",
    "Remote",
    "Servo",
    "DHTSensor",
]
