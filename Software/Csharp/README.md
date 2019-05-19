# GoPiGo3 for .NET Core IoT

You will find a full implantation of GoPiGo3 on [.NET Core IoT repository](https://github.com/dotnet/iot). You will be able to program GoPiGo using C#. The full documentation and example is located into the main repository.

.NET Core is open source. .NET Core is best thought of as 'agile .NET'. Generally speaking it is the same as the Desktop .NET Framework distributed as part of the Windows operating system, but it is a cross platform (Windows, Linux, macOS) and cross architecture (x86, x64, ARM) subset that can be deployed as part of the application (if desired), and thus can be updated quickly to fix bugs or add features. It is a perfect fit for boards like Raspberry running Raspbian. Check the [.NET Core IoT documentation](https://github.com/dotnet/iot/tree/master/Documentation) if you are not familiar with .NET Core.

You will find below the general usage and extract of the full documentation. The .NET Core IoT implementation propose 2 ways to access GoPiGo3: either thru a native drive either thru high level classes. In both cases, you need first to instantiate a GoPiGo class.

## Create a GoPiGo class

The main [GoPiGo3.samples](https://github.com/dotnet/iot/tree/master/src/devices/GoPiGo3/samples) contains a series of test showing how to use every elements of the driver.

Create a ```GoPiGo``` class.

```csharp
// Default on the Raspberry is Bus ID = 0 and Chip Set Select Line = 1 for GoPiGo3
var settings = new SpiConnectionSettings(0, 1)
{
    // 500K is the SPI communication with GoPiGo
    ClockFrequency = 500000,
    Mode = SpiMode.Mode0,
    DataBitLength = 8
};
_goPiGo3 = new GoPiGo(new UnixSpiDevice(settings));
// Do whatever you want, read sensors, set motors, etc
// once finished, and class will be disposed, all motors will be floated and sensors reinitialized
// The SpiDevice will the disposed when GoPiGo will be disposed
```

## Using sensors thru the low level driver

To setup a sensor, you need first to set the type of sensor then you can read the data. The below example read an analogic input on the Grove1 port.

```csharp
_goPiGo.SetGroveType(GrovePort.Grove1, GroveSensorType.Custom);
_goPiGo.SetGroveMode(GrovePort.Grove1, GroveInputOutput.InputAnalog);
var _mode = Port == GrovePort.Grove1 ? GrovePort.Grove1Pin1 : GrovePort.Grove2Pin1;
var thevalue = _goPiGo.GetGroveAnalog(_mode);
```

It is **strongly recommended** to use the high level classes implementing the logic to decode correctly the raw values of sensor like in the previous example. If you want to build your own sensor classes, you can use those low level functions. You need to understand if the Pin1 is used (the yellow cable on Grove) and/or the Pin2 is used (the white cable). And of course, you'll need to know the sequence and how to read/write on those pins. You'll find detailed examples in the ```Sensors``` folder.

## Using motors thru the low level driver

There are many ways you can use motors, either by setting the power, either by reading the encoder, either by setting a degree per second speed. Those 3 examples will show you how to use each of them.

### Making a motor moving depending on the position of another motor

In this example, the motor on port D is used to set the position of the motor A. A simple NXT touch sensor is used to end the sequence when it is pressed.

You can see as well the ```MotorStatus``` classes containing all information on the motor. Flags are useful to understand if you have issues with the power or an overload of the motors. 

To reinitialize the encoder, simply set the offset to the current version like shown in the first 2 lines.

```csharp
_goPiGo3.OffsetMotorEncoder(MotorPort.MotorRight, _goPiGo3.GetMotorEncoder(MotorPort.MotorRight));
_goPiGo3.OffsetMotorEncoder(MotorPort.MotorLeft, _goPiGo3.GetMotorEncoder(MotorPort.MotorLeft));
_goPiGo3.SetMotorPositionKD(MotorPort.MotorLeft);
_goPiGo3.SetMotorPositionKP(MotorPort.MotorLeft);
// Float motor Right
_goPiGo3.SetMotorPower(MotorPort.MotorRight, (byte)MotorSpeed.Float);
// set some limits
_goPiGo3.SetMotorLimits(MotorPort.MotorLeft, 50, 200);
Console.WriteLine("Read Motor Left and Right positions. Press enter stop the test.");
AddLines();
//run until we press enter
while (!Console.KeyAvailable)
{
    var target = _goPiGo3.GetMotorEncoder(MotorPort.MotorRight);
    _goPiGo3.SetMotorPosition(MotorPort.MotorLeft, target);
    var status = _goPiGo3.GetMotorStatus(MotorPort.MotorLeft);
    Console.WriteLine($"MotorLeft Target DPS: {target} Speed: {status.Speed} DPS: {status.Dps} Encoder: {status.Encoder} Flags: {status.Flags}");
    status = _goPiGo3.GetMotorStatus(MotorPort.MotorRight);
    Console.Write($"MotorRight Target DPS: {target} Speed: {status.Speed} DPS: {status.Dps} Encoder: {status.Encoder} Flags: {status.Flags}");
    Thread.Sleep(20);
}
```

## How to use the high level classes

There are high level classes to handle directly sensors like analogic sensors, buzzers, leds, buttons. There is as well a Motor and a Vehicle class to make it easier to pilot and control the motors rather than thru the low level driver.

### Using the Sensor classes

Using the sensor classes is straight forward. Just reference a class and initialized it. Access properties which are common to all sensors, ```Value``` and ```ToString()```. 

Example creating an Ultrasonic sensor on Grove1 port:

```csharp
UltraSonicSensor ultraSonic = new UltraSonicSensor(_goPiGo3, GrovePort.Grove1);
Console.WriteLine($"Test {ultraSonic.SensorName} on port {ultraSonic.Port}. Gives the distance. Press enter to stop the test.");
while (!Console.KeyAvailable)
{                
    Console.CursorLeft = 0;
    Console.Write($"Value: {ultraSonic.Value}, Value as String: {ultraSonic}");
    Thread.Sleep(100);
}
```

### Using Motors

Motors are as well really easy to use. You have functions ```Start()```, ```Stop()```, ```SetSpeed(speed) ``` and ```GetSpeed()``` which as you can expect will start, stop, change the speed and give you the current speed. A speed property is available as well and will change the speed. 

The motors have an encoder which gives you the position the precision can be found in the property ```EncoderTicksPerRotation``` (degree precision). You can get access thru function ```GetTachoCount()```. As the numbers can get big quite fast, you can reset this counter by using ```SetTachoCount(newnumber) ```. A ```TachoCount``` property is available as well. This property like for sensors can raise an event on a minimum time base you can setup.

```csharp
GoPiGo _goPiGo = new GoPiGo();

Motor motor = new Motor(_goPiGo, MotorPort.MotorLeft);
motor.SetSpeed(100); //speed goes from -100 to +100, others will float the motor
motor.Start();
motor.SetSpeed(motor.GetSpeed() + 10);
Console.WriteLine($"Encoder: {motor.GetTachoCount()}");
Console.WriteLine($"Encoder: {motor.TachoCount}"); //same as previous line
Console.WriteLine($"Speed: {motor.GetSpeed()}");
Console.WriteLine($"Speed: {motor.Speed}"); //same as previous line
motor.SetPolarity(Polarity.OppositeDirection); // change the direction
motor.Stop();
```

Here is an example of the ```Vehicle``` class: 

```csharp
Console.WriteLine("Vehicle drive test using Motor A for left, MotorLeft for right, not inverted direction");
Vehicle veh = new Vehicle(_goPiGo, MotorPort.MotorRight, MotorPort.MotorLeft);
veh.DirectionOpposite = true;
Console.WriteLine("Driving backward");
veh.Backward(30, 5000);
Console.WriteLine("Driving forward");
veh.Foreward(30, 5000);
Console.WriteLine("Turning left");
veh.TrunLeftTime(30, 5000);
Console.WriteLine("Turning right");
veh.TrunRightTime(30, 5000);
Console.WriteLine("Turning left");
veh.TurnLeft(30, 180);
Console.WriteLine("Turning right");
veh.TurnRight(30, 180);
```

The ```Vehicle``` class offers functions with timeout allowing to drive for a certain amount of time. All timing are in milliseconds. Turning functions offers as well a degree mode which allows to turn by a certain degree rather than a specific time.
