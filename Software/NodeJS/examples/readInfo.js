const Gopigo = require('../lib/gopigo3');

const gpg = new Gopigo();

try {
    console.log('Manufacturer               :', gpg.getManufacturer());
    console.log('Board                      :', gpg.getBoard());
    console.log('Serial Number              :', gpg.getId());
    console.log('Hardware Version           :', gpg.getVersionHardware());
    console.log('Firmware Version           :', gpg.getVersionFirmware());
    console.log('Battery Voltage            :', gpg.getVoltageBattery());
    console.log('5v Voltage                 :', gpg.getVoltage5v());
} catch (err) {
    console.log(err);
}
