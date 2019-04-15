from I2C_mutex import Mutex
import time

# needed for duck typing
import gopigo3
import operator

mutex = Mutex()

try:
    from di_sensors import easy_line_follower, easy_distance_sensor
    di_sensors_available = True
except ImportError as err:
    di_sensors_available = False
    print(str(err))
except Exception as err:
    di_sensors_available = False
    print(str(err))


def _ifMutexAcquire(mutex_enabled=False):
    """
    Acquires the I2C if the ``use_mutex`` parameter of the constructor was set to ``True``.
    Always acquires if system-wide mutex has been set.

    """
    if mutex_enabled or mutex.overall_mutex()==True:
        mutex.acquire()

def _ifMutexRelease(mutex_enabled=False):
    """
    Releases the I2C if the ``use_mutex`` parameter of the constructor was set to ``True``.
    """
    if mutex_enabled or mutex.overall_mutex()==True:
        mutex.release()

def debug(in_str):
    if False:
        print(in_str)

#############################################################
# SENSORS
#############################################################



class Sensor(object):
    """
    Base class for all sensors. Can only be instantiated through the use of an :py:class:`~easygopigo3.EasyGoPiGo3` object.

    It *should* only be used as a base class for any type of sensor. Since it contains methods for setting / getting the ports or the pinmode,
    it's basically useless unless a derived class comes in and adds functionalities.

    :var str port: There're 4 types of ports - analog, digital, I2C and serial ports. The string identifiers are mapped in the following graphical representation - :ref:`hardware-ports-section`.
    :var str pinmode: Represents the mode of operation of a pin - can be a digital input/output, an analog input/output or even a custom mode which must defined in the `GoPiGo3`_'s firmware.
    :var int pin: Each grove connector has 4 pins: GND, VCC and 2 signal pins that can be user-defined. This variable specifies which pin of these 2 signal pins is used.
    :var int portID: Depending on ``ports``'s value, an ID is given to each port. This variable is not important to us.
    :var str descriptor: Represents the "informal" string representation of an instantiated object of this class.
    :var EasyGoPiGo3 gpg: Object instance of the :py:class:`~easygopigo3.EasyGoPiGo3` class.

    .. note::

        The classes which derive from this class are the following:

             * :py:class:`~easysensors.DigitalSensor`
             * :py:class:`~easysensors.AnalogSensor`
             * :py:class:`~easysensors.Servo`
             * :py:class:`~easysensors.DHTSensor`

        And the classes which are found at 2nd level of inheritance from this class are:

            * :py:class:`~easysensors.LightSensor`
            * :py:class:`~easysensors.SoundSensor`
            * :py:class:`~easysensors.LoudnessSensor`
            * :py:class:`~easysensors.UltraSonicSensor`
            * :py:class:`~easysensors.Buzzer`
            * :py:class:`~easysensors.Led`
            * :py:class:`~easysensors.ButtonSensor`

    .. warning::

        1. This class should only be used by the developers of the `GoPiGo3`_ platform.
        2. The name of this class isn't representative of the devices we connect to the `GoPiGo3`_ robot - we don't only use this class for sensors, but for any kind of device that we can connect to the `GoPiGo3`_ robot.

    """
    PORTS = {}

    def __init__(self, port, pinmode, gpg, use_mutex=False):
        """
        Constructor for creating a connection to one of the available grove ports on the `GoPIGo3`_.

        :param str port: Specifies the port with which we want to communicate / interact with. The string literals we can use for identifying a port are found in the following graphical drawing : :ref:`hardware-ports-section`.
        :param str pinmode: The mode of operation of the pin we're selecting.
        :param easygopigo3.EasyGoPiGo3 gpg: An instantiated object of the :py:class:`~easygopigo3.EasyGoPiGo3` class. We need this :py:class:`~easygopigo3.EasyGoPiGo3` class for setting up the `GoPiGo3`_ robot's pins.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following string values:

             * ``"AD1"`` - for digital and analog ``pinmode``'s.
             * ``"AD2"`` - for digital and analog ``pinmode``'s.
             * ``"SERVO1"`` - for ``"OUTPUT"`` ``pinmode``.
             * ``"SERVO2"`` - for ``"OUTPUT"`` ``pinmode``.
             * ``"I2C"`` - the ``pinmode`` is irrelevant here.
             * ``"SERIAL"`` - the ``pinmode`` is irrelevant here.

        These ports' locations can be seen in the following graphical representation - :ref:`hardware-ports-section`.

        The ``pinmode`` parameter can take the following string values:

             * ``"INPUT"`` - for general purpose inputs. The `GoPiGo3`_ has 12-bit ADCs.
             * ``"DIGITAL_INPUT"`` - for digital inputs. The port can detect either **0** or **1**.
             * ``"OUTPUT"`` - for general purpose outputs.
             * ``"DIGITAL_OUTPUT"`` - for digital outputs. The port can only be set to **0** or **1**.
             * ``"US"`` - that's for the :py:class:`~easysensors.UltraSonicSensor` which can be bought from our `shop`_. Can only be used with ports ``"AD1"`` and ``"AD2"``.
             * ``"IR"`` - that's for the `infrared receiver`_. Can only be used with ports ``"AD1"`` and ``"AD2"``.

        .. warning::

             At the moment, there's no class for interfacing with the `infrared receiver`_.

        """
        debug("Sensor init")

        if not isinstance(gpg, gopigo3.GoPiGo3):
            raise TypeError("Use a GoPiGo3 object for the gpg parameter.")
        self.gpg = gpg
        debug(pinmode)
        self.set_port(port)
        self.set_pin_mode(pinmode)
        self.use_mutex = use_mutex

        self.reconfig_bus()

    def reconfig_bus(self):
        """
        Sets the bus properly. Sometimes this needs to be done even after instantiation when two processes are 
        trying to connect to the GoPiGo and one re-initialises the ports.
        """
        pinmode = self.get_pin_mode()
        try:
            # I2C sensors don't need a valid gpg
            if pinmode == "INPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_INPUT_ANALOG)
            if pinmode == "DIGITAL_INPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_INPUT_DIGITAL)
            if pinmode == "OUTPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_OUTPUT_PWM)
            if pinmode == "DIGITAL_OUTPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_OUTPUT_DIGITAL)
            if pinmode == "US":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.US)
            if pinmode == "IR":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.IR_DI_REMOTE)
        except:
            pass

    def __str__(self):
        """
        Prints out a short summary of the class-instantiated object's attributes.

        :returns: A string with a short summary of the object's attributes.
        :rtype: str

        The returned string is made of the following components:

             * the :py:attr:`~easysensors.Sensor.descriptor`'s description
             * the :py:attr:`~easysensors.Sensor.port` name
             * the :py:attr:`~easysensors.Sensor.pin` identifier
             * the :py:attr:`~easysensors.Sensor.portID` - see :py:meth:`~easysensors.Sensor.set_port` method.

        Sample of returned string as shown in a terminal:

        .. code-block:: console

             $ ultrasonic sensor on port AD1
             $ pinmode OUTPUT
             $ portID 3

        """
        return ("{} on port {} \npinmode {}\nportID {}".format(self.descriptor,
                self.get_port(), self.get_pin_mode(), self.portID))

    def set_pin(self, pin):
        """
        Selects one of the 2 available pins of the grove connector.

        :param int pin: **1** for the exterior pin of the grove connector (aka SIG) or anything else for the interior one.

        """
        if self.port == "AD1":
            if pin == 1:
                self.pin = self.gpg.GROVE_1_1
            else:
                self.pin = self.gpg.GROVE_1_2
        elif self.port == "AD2":
            if pin == 1:
                self.pin = self.gpg.GROVE_2_1
            else:
                self.pin = self.gpg.GROVE_2_2
        debug("setting pin to {}".format(self.pin))

    def get_pin(self):
        """
        Tells us which pin of the grove connector is used.

        :returns: For exterior pins (aka SIG) it returns :py:data:`gopigo3.GROVE_2_1` or :py:data:`gopigo3.GROVE_2_2` and for interior pins (aka NC) it returns :py:data:`gopigo3.GROVE_1_2` or :py:data:`gopigo3.GROVE_1_2`.
        :rtype: int

        """
        return self.pin

    def set_port(self, port):
        """
        Sets the port that's going to be used by our new device. Again, we can't communicate with our
        device, because the class doesn't have any methods for interfacing with it, so we need to create
        a derived class that does this.

        :param str port: The port we're connecting the device to. Take a look at the :ref:`hardware-ports-section`' locations.

        Apart from this graphical representation of the ports' locations (:ref:`hardware-ports-section` locations),
        take a look at the list of ports in :py:meth:`~easysensors.Sensor.__init__`'s description.

        """
        debug(port)
        self.port = port
        debug(self.port)
        debug("self.gpg is {}".format(self.gpg))

        if port == "AD1":
            self.portID = self.gpg.GROVE_1
        elif port == "AD2":
            self.portID = self.gpg.GROVE_2
        elif port == "SERIAL":
            self.portID = -1
        elif port == "I2C":
            self.portID = -2
        elif port == "SERVO1":
            self.portID = self.gpg.SERVO_1
        elif port == "SERVO2":
            self.portID = self.gpg.SERVO_2
        else:
            self.portID = -5

        debug(self.portID)

    def get_port(self):
        """
        Gets the current port our device is connected to.

        :returns: The current set port.
        :rtype: str

        Apart from this graphical representation of the ports' locations (:ref:`hardware-ports-section` locations),
        take a look at the list of ports in :py:meth:`~easysensors.Sensor.__init__`'s description.

        """
        return (self.port)

    def get_port_ID(self):
        """
        Gets the ID of the port we're set to.

        :returns: The ID of the port we're set to.
        :rtype: int

        See more about port IDs in :py:class:`~easysensors.Sensor`'s description.

        """
        return (self.portID)

    def set_pin_mode(self, pinmode):
        """
        Sets the pin mode of the port we're set to.

        :param str pinmode: The pin mode of the port.

        See more about pin modes in :py:meth:`~easysensors.Sensor.__init__`'s description.

        """
        self.pinmode = pinmode

    def get_pin_mode(self):
        """
        Gets the pin mode of the port we're set to.

        :returns: The pin mode of the port.
        :rtype: str

        See more about pin modes in :py:meth:`~easysensors.Sensor.__init__`'s description.

        """
        return (self.pinmode)

    # def is_analog(self):
    #     return (self.pin == ANALOG)

    # def is_digital(self):
    #     return (self.pin == DIGITAL)

    def set_descriptor(self, descriptor):
        """
        Sets the object's description.

        :param str descriptor: The object's description.

        See more about class descriptors in :py:class:`~easysensors.Sensor`'s description.

        """
        self.descriptor = descriptor
##########################


class DigitalSensor(Sensor):
    def __init__(self, port, pinmode, gpg, use_mutex = False):
        debug("DigitalSensor init")
        try:
            Sensor.__init__(self, port, pinmode, gpg, use_mutex)
        except:
            raise("Digital Sensor Init")

    def read(self):
        '''
        Return values:
        0 or 1 are valid values
        -1 may occur when there's a reading error

        On a reading error, a second attempt will be made before
        returning a -1 value
        '''
        try:
            self.value = self.gpg.get_grove_state(self.get_pin())
        except gopigo3.ValueError:
            try:
                self.value = self.gpg.get_grove_state(self.get_pin())
            except Exception:
                return -1

        return self.value

    def write(self, power):
        self.value = power
        # not ported to GPG3 yet
        return -1
        # return gopigo.digitalWrite(self.get_port_ID(), power)
##########################


class AnalogSensor(Sensor):
    """
    Class for analog devices with input/output capabilities on the `GoPiGo3`_ robot.
    This class is derived from :py:class:`~easysensors.Sensor` class, so this means this class inherits all attributes and methods.

    For creating an :py:class:`~easysensors.AnalogSensor` object an :py:class:`~easygopigo3.EasyGoPiGo3` object is needed like in the following example.

    .. code-block:: python

         # initialize an EasyGoPiGo3 object first
         gpg3_obj = EasyGoPiGo3()

         # let's have an analog input sensor on "AD1" port
         port = "AD1"
         pinmode = "INPUT"

         # instantiate an AnalogSensor object
         # pay attention that we need the gpg3_obj
         analogsensor_obj = AnalogSensor(port, pinmode, gpg3_obj)

         # for example
         # read the sensor's value as we have an analog sensor connected to "AD1" port
         analogsensor_obj.read()

    .. warning::

        The name of this class isn't representative of the type of devices we connect to the `GoPiGo3`_ robot.
        With this class, both analog sensors and actuators (output devices such as LEDs which may require controlled output voltages) can be connected.

    """
    def __init__(self, port, pinmode, gpg, use_mutex = False):
        """
        Binds an analog device to the specified ``port`` with the appropriate ``pinmode`` mode.

        :param str port: The port to which the sensor/actuator is connected.
        :param str pinmode: The pin mode of the device that's connected to the `GoPiGo3`_.
        :param easygopigo3.EasyGoPiGo3 gpg: Required object for instantiating an :py:class:`~easysensors.AnalogSensor` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The available ``port``'s for use are the following:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        .. important::

            Since the grove connector allows 2 signals to pass through 2 pins (not concurently), we can select which pin to go with by using the :py:meth:`~easysensors.Sensor.set_pin` method.
            By default, we're using pin **1**, which corresponds to the exterior pin of the grove connector (aka SIG) and the wire is yellow.

        """
        debug("AnalogSensor init")

        self.value = 0
        self.freq = 24000
        self._max_value = 4096
        try:
            Sensor.__init__(self, port, pinmode, gpg, use_mutex)
        except:
            raise("AnalogSensor Init")

        # select the outwards pin of the grove connector
        self.set_pin(1)

        # this delay is at least needed by the Light sensor
        time.sleep(0.01)

    def read(self):
        """
        Reads analog value of the sensor that's connected to our `GoPiGo3`_ robot.

        :returns: 12-bit number representing the voltage we get from the sensor. Range goes from 0V-5V.
        :rtype: int
        :raises gopigo3.ValueError: If an invalid value was read.
        :raises Exception: If any other errors happens.

        """
        try:
            self.value = self.gpg.get_grove_analog(self.get_pin())
        except gopigo3.ValueError as e:
            try:
                self.value = self.gpg.get_grove_analog(self.get_pin())
            except Exception as e:
                print("Value Error: {}".format(e))
                return 0
        except Exception as e:
            print("Analog Read fail-all: {}".format(e))
        # print("Analog Read: {}".format(self.value))
        return self.value

    def percent_read(self):
        """
        Reads analog value of the sensor that's connected to our `GoPiGo3`_ robot as a percentage.

        :returns: Percentage mapped to 0V-5V range.
        :rtype: int

        """
        reading_percent = round(self.read() * 100 // self._max_value)

        # Some sensors - like the loudness_sensor -
        # can actually return higher than 100% so let's clip it
        # and keep classrooms within an acceptable noise level
        if reading_percent > 100:
            reading_percent = 100
        return reading_percent

    def write(self, power):
        """
        Generates a PWM signal on the selected port.
        Good for simulating an DAC convertor - for instance an LED is a good candidate.

        :param int power: Number from **0** to **100** that represents the duty cycle as a percentage of the frequency's period.

        .. tip::

             If the ``power`` parameter is out of the given range, the most close and valid value will be selected.


        """
        self.value = power
        return_value = self.gpg.set_grove_pwm_duty(self.get_pin(),
                                                       power)
        return return_value

    def write_freq(self, freq):
        """
        Sets the frequency of the PWM signal.

        The frequency range goes from 3Hz up to 48000Hz. Default value is set to 24000Hz (24kHz).

        :param int freq: Frequency of the PWM signal.

        .. seealso::

            Read more about this in :py:meth:`gopigo3.GoPiGo3.set_grove_pwm_frequency`'s description.

        """
        self.freq = freq
        # debug("write_freq: {}".format(self.freq))
        return_value = self.gpg.set_grove_pwm_frequency(
                self.get_port_ID(),
                self.freq)
        debug ("Analog Write on {} at {}".format(self.get_port_ID(),
                                                     self.freq))
        return return_value
##########################


class LightSensor(AnalogSensor):
    """
    Class for the `Grove Light Sensor`_.

    This class derives from :py:class:`~easysensors.AnalogSensor` class, so all of its attributes and methods are inherited.
    For creating a :py:class:`~easysensors.LightSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_light_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a LightSensor object through the gpg3_obj object
         light_sensor = gpg3_obj.init_light_sensor()

         # do the usual stuff, like read the data of the sensor
         value = light_sensor.read()
         value_percentage = light_sensor.percent_read()

         # take a look at AnalogSensor class for more methods and attributes

    Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the Light Sensor connected to
         port = "AD2"

         light_sensor = gpg3_obj.init_light_sensor(port)

         # read the sensor the same way as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.

    """
    def __init__(self, port="AD1", gpg=None, use_mutex = False):
        """
        Constructor for initializing a :py:class:`~easysensors.LightSensor` object for the `Grove Light Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Light Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.LightSensor` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        debug("LightSensor init")
        self.set_descriptor("Light sensor")
        try:
            AnalogSensor.__init__(self, port, "INPUT", gpg, use_mutex)
        except:
            raise
        self.set_pin(1)
##########################


class SoundSensor(AnalogSensor):
    """
    Class for the `Grove Sound Sensor`_.

    This class derives from :py:class:`~easysensors.AnalogSensor` class, so all of its attributes and methods are inherited.
    For creating a :py:class:`~easysensors.SoundSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_sound_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a SoundSensor object through the gpg3_obj object
         sound_sensor = gpg3_obj.init_sound_sensor()

         # do the usual stuff, like read the data of the sensor
         value = sound_sensor.read()
         value_percentage = sound_sensor.percent_read()

         # take a look at AnalogSensor class for more methods and attributes

    | Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the sound sensor connected to
         port = "AD1"

         sound_sensor = gpg3_obj.init_sound_sensor(port)

         # read the sensor the same way as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.

    """
    def __init__(self, port="AD1", gpg=None, use_mutex=False):
        """
        Constructor for initializing a :py:class:`~easysensors.SoundSensor` object for the `Grove Sound Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Sound Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.SoundSensor` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        debug("Sound Sensor on port " + port)
        self.set_descriptor("Sound sensor")
        try:
            AnalogSensor.__init__(self, port, "INPUT", gpg, use_mutex)
        except:
            raise
        self.set_pin(1)


##########################

class LoudnessSensor(AnalogSensor):
    """
    Class for the `Grove Loudness Sensor`_.

    This class derives from :py:class:`~easysensors.AnalogSensor` class, so all of their attributes and methods are inherited.
    For creating a :py:class:`~easysensors.LoudnessSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_loudness_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a LoudnessSensor object through the gpg3_obj object
         loudness_sensor = gpg3_obj.init_loudness_sensor()

         # do the usual stuff, like read the data of the sensor
         value = loudness_sensor.read()
         value_percentage = loudness_sensor.percent_read()

         # take a look at AnalogSensor class and Sensor class for more methods and attributes

    Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the sound sensor connected to
         port = "AD1"

         loudness_sensor = gpg3_obj.init_loudness_sensor(port)

         # read the sensor the same way as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.

    """
    def __init__(self, port="AD1", gpg=None, use_mutex=False):
        """
        Constructor for initializing a :py:class:`~easysensors.LoudnessSensor` object for the `Grove Loudness Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Loudness Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.LoudnessSensor` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        debug("Loudness Sensor on port " + port)
        self.set_descriptor("Loudness sensor")
        try:
            AnalogSensor.__init__(self, port, "INPUT", gpg, use_mutex)
        except:
            raise
        # time.sleep(0.2)
        self.set_pin(1)
        self._max_value = 1024  # based on empirical tests

##########################

class UltraSonicSensor(AnalogSensor):
    """
    Class for the `Grove Ultrasonic Sensor`_.

    This class derives from :py:class:`~easysensors.AnalogSensor` class, so all of its attributes and methods are inherited.
    For creating a :py:class:`~easysensors.UltraSonicSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_ultrasonic_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a UltraSonicSensor object through the gpg3_obj object
         ultrasonic_sensor = gpg3_obj.init_ultrasonic_sensor()

         # do the usual stuff, like read the distance the sensor is measuring
         distance_cm = ultrasonic_sensor.read()
         distance_inches = ultrasonic_sensor.read_inches()

         # take a look at AnalogSensor class for more methods and attributes

    Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the ultrasonic sensor connected to
         port = "AD1"

         ultrasonic_sensor = gpg3_obj.init_ultrasonic_sensor(port)

         # read the sensor's measured distance as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    def __init__(self, port="AD1", gpg=None, use_mutex = False):
        """
        Constructor for initializing a :py:class:`~easysensors.UltraSonicSensor` object for the `Grove Ultrasonic Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Ultrasonic Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.UltraSonicSensor` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """

        try:
            debug("Ultrasonic Sensor on port " + port)
            AnalogSensor.__init__(self, port, "US", gpg, use_mutex)
            self.set_descriptor("Ultrasonic sensor")
            self.safe_distance = 500
            self.set_pin(1)
        except:
            raise


    def is_too_close(self):
        """
        Checks whether the `Grove Ultrasonic Sensor`_ measures a distance that's too close to a target than
        what we consider a *safe distance*.

        :returns: Whether the `Grove Ultrasonic Sensor`_ is too close from a target.
        :rtype: bool
        :raises gopigo3.SensorError: If a sensor is not yet configured when trying to read it.

        A *safe distance* can be set with the :py:meth:`~easysensors.UltraSonicSensor.set_safe_distance` method.

        .. note::

            The default *safe distance* is set at 50 cm.


        """
        try:
            val = self.gpg.get_grove_value(self.get_port_ID())
        except gopigo3.SensorError as e:
            print("Invalid Reading")
            print(e)
            return False

        if  val < self.get_safe_distance():
            return True
        return False

    def set_safe_distance(self, dist):
        """
        Sets a *safe distance* for the `Grove Ultrasonic Sensor`_.

        :param int dist: Minimum distance from a target that we can call a *safe distance*.

        To check whether the robot is too close from a target, please check the :py:meth:`~easysensors.UltraSonicSensor.is_too_close` method.

        .. note::

            The default *safe distance* is set at 50 cm.


        """
        self.safe_distance = int(dist)

    def get_safe_distance(self):
        """
        Gets what we call the *safe distance* for the `Grove Ultrasonic Sensor`_.

        :returns: The minimum distance from a target that can be considered a *safe distance*.
        :rtype: int

        .. note::

            The default *safe distance* is set at 50 cm.

        """
        return self.safe_distance

    def read_mm(self):
        """
        Measures the distance from a target in millimeters.

        :returns: The distance from a target in millimeters.
        :rtype: int
        :raises gopigo3.ValueError: If trying to read an invalid value.
        :raises Exception: If any other error occurs.

        .. important::

            * This method can read distances between **15-4300** millimeters.
            * This method will read the data for 3 times and it'll discard anything that's smaller than 15 millimeters and bigger than 4300 millimeters.
            * If data is discarded 5 times (due to a communication error with the sensor), then the method returns **5010**.

        """
        return_reading = 0
        readings = []
        skip = 0
        value=0

        while len(readings) < 3 and skip < 5:
            try:
                value = self.gpg.get_grove_value(self.get_port_ID())
                print ("raw {}".format(value))
            except gopigo3.ValueError as e:
                # print("Value Error")
                # print(e)
                value = 5010   # assume open road ahead
                time.sleep(0.05)

            except Exception as e:
                print(e)
                skip += 1
                time.sleep(0.05)
                continue

            if value <= 4300 and value >= 15:
                readings.append(value)
                # debug (readings)
            else:
                skip += 1

        if skip >= 5:
            # if value = 0 it means Ultrasonic Sensor wasn't found
            if value == 0:
                return(0)

            # no special meaning to the number 5010
            return(5010)

        for reading in readings:
            return_reading += reading

        return_reading = int(return_reading / len(readings))

        return (return_reading)

    def read(self):
        """
        Measures the distance from a target in centimeters.

        :returns: The distance from a target in centimeters.
        :rtype: int

        .. important::

            * This method can read distances between **2-430** centimeters.
            * If data is discarded 5 times (due to a communication error with the sensor), then the method returns **501**.

        """
        # returns value in cm
        value = self.read_mm()
        if value >= 15 and value <= 5010:
            return int(round(value / 10.0))
        return value

    def read_inches(self):
        """
        Measures the distance from a target in inches.

        :returns: The distance from a target in inches.
        :rtype: float (one decimal)

        .. important::

            * This method can read distances of up to **169** inches.
            * If data is discarded 5 times (due to a communication error with the sensor), then the method returns **501**.

        """
        value = self.read()   # cm reading
        if value == 501:
            return 501
        return (round(value / 2.54, 1))
##########################


class Buzzer(AnalogSensor):
    """
    Class for the `Grove Buzzer`_.

    This class derives from :py:class:`~easysensors.AnalogSensor` class, so all of its attributes and methods are inherited.
    For creating a :py:class:`~easysensors.Buzzer` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_buzzer` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a UltraSonicSensor object through the gpg3_obj object
         buzzer = gpg3_obj.init_buzzer()

         # turn on and off the buzzer
         buzzer.sound_on()
         sleep(1)
         buzzer.sound_off()

         # take a look at AnalogSensor class for more methods and attributes

    If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the ultrasonic sensor connected to
         port = "AD1"

         buzzer = gpg3_obj.init_buzzer(port)

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    #:Dictionary of frequencies for each musical note.
    #:For instance, ``scale["A3"]`` instruction is equal to 220 Hz (that's the A3 musical note's frequency).
    #:This dictionary is useful when we want to make the buzzer ring at certain frequencies (aka musical notes).
    scale = {"A3": 220,
             "A3#": 233,
             "B3": 247,
             "C4": 261,
             "C4#": 277,
             "D4": 293,
             "D4#": 311,
             "E4": 329,
             "F4": 349,
             "F4#": 370,
             "G4": 392,
             "G4#": 415,
             "A4": 440,
             "A4#": 466,
             "B4": 494,
             "C5": 523,
             "C5#": 554,
             "D5": 587,
             "D5#": 622,
             "E5": 659,
             "F5": 698,
             "F5#": 740,
             "G5": 784,
             "G5#": 831}

    def __init__(self, port="AD1", gpg=None, use_mutex = False):
        """
        Constructor for initializing a :py:class:`~easysensors.Buzzer` object for the `Grove Buzzer`_.

        :param str port = "AD1": Port to which we have the `Grove Buzzer`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.Buzzer` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :var int power = 50: Duty cycle of the signal that's put on the buzzer.
        :var int freq = 329: Frequency of the signal that's put on the buzzer. 329Hz is synonymous to E4 musical note. See :py:attr:`~.easysensors.Buzzer.scale` for more musical notes.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """

        try:
            AnalogSensor.__init__(self, port, "OUTPUT", gpg, use_mutex)
            self.set_pin(1)
            self.set_descriptor("Buzzer")
            self.power = 50
            self.freq = 329
            self.sound_off()
        except:
            raise

    def sound(self, freq):
        """
        Sets a musical note for the `Grove Buzzer`_.

        :param int freq: The frequency of the signal that's put on the `Grove Buzzer`_.

        For a list of musical notes, please see :py:attr:`~.easysensors.Buzzer.scale`.
        See this example script on how to play musical notes.

        .. code-block:: python

             # initialize all the required objects and connect the sensor to the GoPiGo3

             musical_notes = buzzer.scale
             notes_i_want_to_play = {"F4#", "F4#", "C5#", "B3", "B3", "B3"}
             wait_time = 1.0

             for note in notes_i_want_to_play:
                buzzer.sound(musical_notes[note])
                sleep(wait_time)

                # enjoy the musical notes

        """
        try:
            freq = int(freq)
        except:
            freq = 0

        # limit duty cycles (aka power) values to either 0 or 50
        if freq <= 0:
            power = 0
            freq = 0
        else:
            power = 50

        # if buzzer has to emit a sound then set frequency
        if power == 50:
            # translation_factor = ((40000 - 20) / 100)
            # freq = (freq * translation_factor) + 20
            self.write_freq(freq)

        # debug(freq, power)
        # set duty cycle, either 0 or 50
        self.write(power)

    def sound_off(self):
        """
        Turns off the `Grove Buzzer`_.

        """
        self.sound(0)

    def sound_on(self):
        """
        Turns on the `Grove Buzzer`_ at the set frequency.

        For changing the frequency, please check the :py:meth:`~easysensors.Buzzer.sound` method.

        """
        self.sound(self.freq)
##########################


class Led(AnalogSensor):
    """
    Class for the `Grove LED`_.

    With this class the following things can be done:

         * Turn *ON*/*OFF* an LED.
         * Set a level of brightness for the LED.
         * Check if an LED is turned *ON* or *OFF*.

    This class derives from :py:class:`~easysensors.AnalogSensor` class, so all of its attributes and methods are inherited.
    For creating a :py:class:`~easysensors.Led` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_led` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a Led object through the gpg3_obj object
         led = gpg3_obj.init_led()

         # turn on and off the buzzer
         led.light_max()
         sleep(1)
         led.light_off()

         # take a look at AnalogSensor class for more methods and attributes

    If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the led connected to
         port = "AD1"

         led = gpg3_obj.init_led(port)

         # call some Led-specific methods

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """
    def __init__(self, port="AD1", gpg=None, use_mutex = False):
        """
        Constructor for initializing a :py:class:`~easysensors.Led` object for the `Grove LED`_.

        :param str port = "AD1": Port to which we have the `Grove LED`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.Led` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("LED")
            AnalogSensor.__init__(self, port, "OUTPUT", gpg, use_mutex)
            self.set_pin(1)
        except:
            raise

    def light_on(self, power):
        """
        Sets the duty cycle for the `Grove LED`_.

        :param int power: Number between **0** and **100** that represents the duty cycle of PWM signal.

        """
        self.write(power)

    def light_max(self):
        """
        Turns on the `Grove LED`_ at full power.

        """
        max_power = 100
        self.light_on(max_power)

    def light_off(self):
        """
        Turns off the `Grove LED`_.

        """
        self.write(0)

    def is_on(self):
        """
        Checks if the `Grove LED`_ is turned on.

        :returns: If the `Grove LED`_ is on.
        :rtype: bool

        """
        return (self.value > 0)

    def is_off(self):
        """
        Checks if the `Grove LED`_ is turned off.

        :returns: If the `Grove LED`_ is off.
        :rtype: bool

        """
        return (self.value == 0)
##########################


class MotionSensor(DigitalSensor):
    """
    Class for the `Grove Motion Sensor`_.

    This class derives from :py:class:`~easysensors.Sensor` (check for throwable exceptions) and :py:class:`~easysensors.DigitalSensor` classes, so all attributes and methods are inherited.
    For creating a :py:class:`~easysensors.MotionSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_motion_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a Motion Sensor object through the gpg3_obj object on default port AD1
         motion_sensor = gpg3_obj.init_motion_sensor()

         while True:
             if motion_sensor.motion_detected():
                 print("motion detected")
             else:
                 print("no motion")

         # take a look at DigitalSensor & Sensor class for more methods and attributes

    If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the motion sensor connected to
         port = "AD2"

         motion_sensor = gpg3_obj.init_motion_sensor(port)

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    def __init__(self, port="AD1", gpg=None, use_mutex = False):
        """
        Constructor for initializing a :py:class:`~easysensors.MotionSensor` object for the `Grove Motion Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Motion Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.MotionSensor` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("Motion Sensor")
            DigitalSensor.__init__(self, port, "DIGITAL_INPUT", gpg, use_mutex)
            self.set_pin(1)
        except:
            raise

    def motion_detected(self,port="AD1"):
        """
        Checks if the `Grove Motion Sensor`_ detects a motion.

        :returns: ``True`` or ``False``, if the `Grove Motion Sensor`_ detects a motion or not.
        :rtype: bool

        """
        return self.read() == 1
##########################


class ButtonSensor(DigitalSensor):
    """
    Class for the `Grove Button`_.

    This class derives from :py:class:`~easysensors.Sensor` (check for throwable exceptions) and :py:class:`~easysensors.DigitalSensor` classes, so all attributes and methods are inherited.
    For creating a :py:class:`~easysensors.ButtonSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_button_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a Button object through the gpg3_obj object
         button = gpg3_obj.init_button_sensor()

         while True:
             if button.is_button_pressed():
                 print("button pressed")
             else:
                 print("button released")

         # take a look at DigitalSensor & Sensor class for more methods and attributes

    If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the button connected to
         port = "AD1"

         button = gpg3_obj.init_button_sensor(port)

         # call some button-specific methods

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    def __init__(self, port="AD1", gpg=None, use_mutex = False):
        """
        Constructor for initializing a :py:class:`~easysensors.ButtonSensor` object for the `Grove Button`_.

        :param str port = "AD1": Port to which we have the `Grove Button`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easysensors.Button` object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("Button sensor")
            DigitalSensor.__init__(self, port, "DIGITAL_INPUT", gpg, use_mutex)
            self.set_pin(1)
        except Exception as e:
            print("button init: {}".format(e))
            raise

    def is_button_pressed(self):
        """
        Checks if the `Grove Button`_ is pressed.

        :returns: ``True`` or ``False``, if the `Grove Button`_ is pressed.
        :rtype: bool

        """
        return self.read() == 1
##########################


class Remote(Sensor):
    """
    Class for interfacing with the `Infrared Receiver`_.

    With this sensor, you can command your `GoPiGo3`_ with an `Infrared Remote`_.

    In order to create an object of this class, we would do it like in the following example.

    .. code-block:: python

        # initialize an EasyGoPiGo3 object
        gpg3_obj = EasyGoPiGo3()

        # now initialize a Remote object
        remote_control = gpg3_obj.init_remote()

        # read whatever command you want from the remote by using
        # the [remote_control] object

    """

    #: List for mapping the codes we get with the :py:meth:`~easysensors.Remote.read` method to
    #: the actual symbols we see on the `Infrared Remote`_.
    keycodes = ["up", "left", "ok", "right","down","1","2","3","4","5","6","7", "8","9","*","0","#"]

    def __init__(self, port="AD1", gpg=None, use_mutex=False):
        """
        Constructor for initializing a :py:class:`~easysensors.Remote` object.

        :param str port = "AD1": The port to which we connect the `Infrared Receiver`_.
        :param easygopigo3.EasyGoPiGo3 gpg = None: The :py:class:`~easygopigo3.EasyGoPiGo3` object that we need for instantiating this object.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``"AD1"`` and ``"AD2"`` ports' location on the `GoPiGo3`_ robot can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("Remote Control")
            Sensor.__init__(self, port, "IR", gpg, use_mutex)
        except:
            raise

    def read(self):
        """
        Reads the numeric code received by the `Infrared Receiver`_.

        :return: The numeric code of the symbol that was pressed on the `Infrared Remote`_.
        :rtype: int

        The numeric code represents the index of the :py:attr:`~easysensors.Remote.keycodes` list.
        By accessing the :py:attr:`~easysensors.Remote.keycodes` elements with the numeric code, you
        get the symbol that was pressed on the `Infrared Remote`_.

        For only getting the symbol that was pressed on the `Infrared Remote`_, please check the :py:meth:`~easysensors.Remote.get_remote_code` method.

        .. warning::

           On :py:class:`~gopigo3.SensorError` exception:

            * ``"Invalid Reading"`` string is printed in the console.
            * The value of **-1** is returned.

        """
        try:
            _ifMutexAcquire(self.use_mutex)
            val = self.gpg.get_grove_value(self.get_port_ID())
            _ifMutexRelease(self.use_mutex)
            return val
        except gopigo3.SensorError as e:
            print("Invalid Reading")
            print(e)
            return -1


    def get_remote_code(self):
        """
        Returns the symbol of the pressed key in a string format.

        :return: The symbol that was pressed on the `Infrared Remote`_.
        :rtype: str

        Check the :py:attr:`~easysensors.Remote.keycodes` list for seeing what strings this method can return.
        On error or when nothing is read, an empty string is returned.

        """
        string = ""
        key = self.read()

        if key > 0 and key < len(self.keycodes)+1:
            string = self.keycodes[self.read()-1]
 
        return string
##########################


class Servo(Sensor):
    """
    Class for controlling `servo`_ motors with the `GoPiGo3`_ robot.
    Allows you to rotate the servo by serving the angle of rotation.

    This class is derived from :py:class:`~easysensors.Sensor` class and because of this, it inherits all the attributes and methods.

    For creating a :py:class:`~easysensors.Servo` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_servo` method like in
    the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now let's instantiate a Servo object through the gpg3_obj object
         # this will bind a servo to port "SERVO1"
         servo = gpg3_obj.init_servo()

         # rotate the servo at 160 degrees
         servo.rotate_servo(160)

    Or if we want to specify the port to which we connect the servo, we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_servo` the following way.

    .. code-block:: python

         servo = gpg3_obj.init_servo("SERVO2")

    .. seealso::

        For more sensors, please see our Dexter Industries `shop`_.

    """

    def __init__(self, port="SERVO1", gpg=None, use_mutex=False):
        """
        Constructor for instantiating a :py:class:`~easysensors.Servo` object for a (or multiple) `servo`_ (servos).

        :param str port = "SERVO1": The port to which we have connected the `servo`_.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object that we need for instantiation.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The available ports that can be used for a `servo`_ are:

             * ``"SERVO1"`` - servo controller port.
             * ``"SERVO2"`` - servo controller port.

        To see where these 2 ports are located, please take a look at the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("GoPiGo3 Servo")
            Sensor.__init__(self, port, "OUTPUT", gpg, use_mutex)
        except:
            raise

    def rotate_servo(self, servo_position):
        """
        Rotates the `servo`_ at a specific angle.

        :param int servo_position: Angle at which the servo has to rotate. The values can be anywhere from **0** to **180** degrees.

        The pulse width varies the following way:

             * **575 uS** for **0 degrees** - the servo's default position.
             * **24250 uS** for **180 degrees** - where the servo is rotated at its maximum position.

        Each rotation of **1 degree** requires an increase of the pulse width by **10.27 uS**.

        .. warning::

             | We use PWM signals (Pulse Width Modulation), so the angle at which a `servo`_ will rotate will be case-dependent.
             | This means a servo's 180 degrees position won't be the same as with another servo.

        """

        #Pulse width range in us corresponding to 0 to 180 degrees
        PULSE_WIDTH_RANGE=1850

        # Servo Position in degrees
        if servo_position > 180:
            servo_position = 180
        elif servo_position < 0:
            servo_position = 0

        pulsewidth = round( (1500-(PULSE_WIDTH_RANGE/2)) +
                            ((PULSE_WIDTH_RANGE /180) * servo_position))

        # Set position for the servo
        self.gpg.set_servo( self.portID, int(pulsewidth))

    def reset_servo(self):
        """
        Resets the `servo`_ straight ahead, in the middle position.

        .. tip::

           | Same as calling ``rotate_servo(90)``.
           | Read more about :py:meth:`~easysensors.Servo.rotate_servo` method.

        """
        self.rotate_servo(90)

    def disable_servo(self):
        """
        Disable (or "float") the `servo`_. 
        
        The effect of this command is that if you then try to rotate the servo manually, it won't resist you, thus meaning that it's not trying to hold a target position.
        """
        self.gpg.set_servo(self.portID, 0)


class DHTSensor(Sensor):
    """
    Class for interfacing with the `Grove DHT Sensor`_.
    This class derives from :py:class:`~easysensors.Sensor` class, so all of its attributes and methods are inherited.

    We can create a :py:class:`~easysensors.DHTSensor` object similar to how we create it in the following template.

    .. code-block:: python

        # create an EasyGoPiGo3 object
        gpg3_obj = EasyGoPiGo3()

        # and now let's instantiate a DHTSensor object through the gpg3_obj object
        dht_sensor = gpg3_obj.init_dht_sensor()

        # read values continuously and print them in the terminal
        while True:
            temp, hum = dht_sensor.read()

            print("temp = {:.1f} hum = {:.1f}".format(temp, hum))
    """

    def __init__(self, gpg=None, sensor_type=0, use_mutex=False):
        """
        Constructor for creating a :py:class:`~easysensors.DHTSensor` object which can be used for interfacing with the `Grove DHT Sensor`_.

        :param easygopigo3.EasyGoPiGo3 gpg = None: Object that's required for instantianting a :py:class:`~easysensors.DHTSensor` object.
        :param int sensor_type = 0: Choose ``sensor_type = 0`` when you have the blue-coloured DHT sensor or ``sensor_type = 1`` when it's white.
        :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes have to be used.
        :raises: Any of the :py:class:`~easysensors.Sensor` constructor's exceptions in case of error.

        """

        self.sensor_type = sensor_type
        port = "SERIAL"

        if self.sensor_type == 0:
            self.set_descriptor("Blue DHT Sensor")
        else:
            self.set_descriptor("White DHT Sensor")

        try:
            Sensor.__init__(self,port,"INPUT",gpg, use_mutex)
        except:
            raise


    def read_temperature(self):
        """
        Return the temperature in Celsius degrees.

        :returns: The temperature in Celsius degrees.
        :rtype: float

        If the sensor isn't plugged in, a ``"Bad reading, try again"`` message is returned.
        If there is a runtime error, then a ``"Runtime error"`` message is returned.

        """

        from di_sensors import DHT

        _ifMutexAcquire(self.use_mutex)
        try:
            temp = DHT.dht(self.sensor_type)[0]
        except Exception:
            raise
        finally:
            _ifMutexRelease(self.use_mutex)

        if temp == -2:
            return "Bad reading, try again"
        elif temp == -3:
            return "Runtime error"
        else:
            # print("Temperature = %.02fC"%temp)
            return temp

    def read_humidity(self):
        """
        Return the humidity as a percentage.

        :returns: Return the humidity as a percentage number from 0% to 100%.
        :rtype: float

        If the sensor isn't plugged in, a ``"Bad reading, try again"`` message is returned.
        If there is a runtime error, then a ``"Runtime error"`` message is returned.

        """
        from di_sensors import DHT

        _ifMutexAcquire(self.use_mutex)
        try:
            humidity = DHT.dht(self.sensor_type)[1]
        except Exception:
            raise
        finally:
            _ifMutexRelease(self.use_mutex)

        if humidity == -2:
            return "Bad reading, try again"
        elif humidity == -3:
            return "Runtime error"
        else:
            # print("Humidity = %.02f%%"%humidity)
            return humidity

    def read(self):
        """
        Return the temperature and humidity.

        :returns: The temperature and humidity as a tuple, where the temperature is the 1st element of the tuple and the humidity the 2nd.
        :rtype: (float, float)

        If the sensor isn't plugged in, a ``"Bad reading, try again"`` message is returned.
        If there is a runtime error, then a ``"Runtime error"`` message is returned.

        """
        from di_sensors import DHT

        _ifMutexAcquire(self.use_mutex)
        try:
            [temp, humidity]=DHT.dht(self.sensor_type)
        except Exception:
            raise
        finally:
            _ifMutexRelease(self.use_mutex)

        if temp ==-2.0 or humidity == -2.0:
            return "Bad reading, try again"
        elif temp ==-3.0 or humidity == -3.0:
            return "Runtime error"
        else:
            return [temp, humidity]


def LineFollower(port="I2C", gpg=None, use_mutex=False):
    """
    Returns an instantiated object of :py:class:`di_sensors.easy_line_follower.EasyLineFollower`. 

    This is a replacement function for the line follower class that used to be found here - it has not moved to :py:mod:`di_sensors` library.

    :param str port = "I2C": The port to which we have connected the line follower sensor. Can also be ``"AD1"``/``"AD2"`` for the `Line Follower`_ sensor.
    :param easygopigo3.EasyGoPiGo3 gpg = None: This is no longer required. Just skip this parameter.
    :param bool use_mutex = False: When using multiple threads/processes that access the same resource/device, mutexes should be enabled.
    :raises ImportError: If the ``di_sensors`` library couldn't be found.
    :raises IOError: If the line follower is not responding.

    """
    if di_sensors_available is False:
        raise ImportError("di_sensors library not available")

    lf = easy_line_follower.EasyLineFollower(port, use_mutex=use_mutex)
    if lf._sensor_id == 0:
        raise OSError("line follower is not reachable")

    return lf
        
##########################


# class RgbLcd(Sensor):
#     '''
#     Wrapper to display Text, change background color on RGB LCD.
#     Connect the sensor to the I2C Port.
#     '''

#     def __init__(self, port="I2C",gpg=None):
#         try:
#             Sensor.__init__(self, port, "OUTPUT",gpg)
#             self.set_descriptor("Grove RGB Lcd")
#         except:
#             raise ValueError("Grove RGB Lcd not found")

#     def display_text(self,text):
#         '''
#         To display a text. It moves to the next line when it encounters "\n" in the text or if there are more than 16 characters.
#         Input the text as a string.
#         '''

#         grove_rgb_lcd.setText(text)

#     # Displays Text over the previous screen without clearing the screen
#     def display_text_over(self,text):
#         grove_rgb_lcd.setText_norefresh(text)

#     def set_BgColor(self,red,green,blue):
#         '''
#         To set the background color of the LCD
#         Red, Green and Blue variables range between (0-255) which indicate the intensity of the color
#         '''
#         grove_rgb_lcd.setRGB(red,green,blue)


if __name__ == '__main__':
    print("No default test")
