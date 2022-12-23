/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  C++ drivers for the GoPiGo3
 */

#include <GoPiGo3.h>

GoPiGo3::GoPiGo3(){
  if(spi_file_handle < 0){
    if(spi_setup()){
      fatal_error("spi_setup error");
    }
  }
  Address = 8;

  load_robot_constants();
}

int GoPiGo3::spi_read_8(uint8_t msg_type, uint8_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(5, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = spi_array_in[4];
  return ERROR_NONE;
}

int GoPiGo3::spi_read_16(uint8_t msg_type, uint16_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(6, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = ((spi_array_in[4] << 8) | spi_array_in[5]);
  return ERROR_NONE;
}

int GoPiGo3::spi_read_32(uint8_t msg_type, uint32_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(8, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = ((spi_array_in[4] << 24) | (spi_array_in[5] << 16) | (spi_array_in[6] << 8) | spi_array_in[7]);
  return ERROR_NONE;
}

int GoPiGo3::spi_read_string(uint8_t msg_type, char *str, uint8_t chars){
  if((chars + 4) > LONGEST_SPI_TRANSFER){
    return -3;
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(chars + 4, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  for(uint8_t i = 0; i < chars; i++){
    str[i] = spi_array_in[i + 4];
  }
  return ERROR_NONE;
}

int GoPiGo3::spi_write_32(uint8_t msg_type, uint32_t value){
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  spi_array_out[2] = ((value >> 24) & 0xFF);
  spi_array_out[3] = ((value >> 16) & 0xFF);
  spi_array_out[4] = ((value >> 8) & 0xFF);
  spi_array_out[5] = (value & 0xFF);
  return spi_transfer_array(6, spi_array_out, spi_array_in);
}

int GoPiGo3::detect(bool critical){
  char ErrorStr[100];
  char str[21];
  int error;
  // assign error to the value returned by get_manufacturer, and if not 0:
  if(error = get_manufacturer(str)){
    if(critical){
      fatal_error("detect error: get_manufacturer failed. Perhaps the GoPiGo3 is not connected, or the address is incorrect.");
    }else{
      return error;
    }
  }
  if(strstr(str, "Dexter Industries") != str){
    if(critical){
      fatal_error("detect error: get_manufacturer string is not 'Dexter Industries'");
    }else{
      return ERROR_WRONG_MANUFACTURER;
    }
  }

  // assign error to the value returned by get_board, and if not 0:
  if(error = get_board(str)){
    if(critical){
      fatal_error("detect error: get_board failed");
    }else{
      return error;
    }
  }
  if(strstr(str, "GoPiGo3") != str){
    if(critical){
      fatal_error("detect error: get_board string is not 'GoPiGo3'");
    }else{
      return ERROR_WRONG_DEVICE;
    }
  }

  // assign error to the value returned by get_version_firmware, and if not 0:
  if(error = get_version_firmware(str)){
    if(critical){
      fatal_error("detect error: get_version_firmware failed");
    }else{
      return error;
    }
  }
  if(strstr(str, FIRMWARE_VERSION_REQUIRED) != str){
    if(critical){
      sprintf(ErrorStr, "error: GoPiGo3 firmware needs version %sx is currently version %s", FIRMWARE_VERSION_REQUIRED, str);
      fatal_error(ErrorStr);
    }else{
      return ERROR_FIRMWARE_MISMATCH;
    }
  }
  return ERROR_NONE;
}

int GoPiGo3::get_manufacturer(char *str){
  return spi_read_string(GPGSPI_MESSAGE_GET_MANUFACTURER, str);
}

int GoPiGo3::get_board(char *str){
  return spi_read_string(GPGSPI_MESSAGE_GET_NAME, str);
}

int GoPiGo3::get_version_hardware(char *str){
  uint32_t value;
  // assign error to the value returned by spi_read_32, and if not 0:
  if(int error = spi_read_32(GPGSPI_MESSAGE_GET_HARDWARE_VERSION, value)){
    return error;
  }
  sprintf(str, "%d.x.x", (value / 1000000));
  return ERROR_NONE;
}

int GoPiGo3::get_version_firmware(char *str){
  uint32_t value;
  // assign error to the value returned by spi_read_32, and if not 0:
  if(int error = spi_read_32(GPGSPI_MESSAGE_GET_FIRMWARE_VERSION, value)){
    return error;
  }
  sprintf(str, "%d.%d.%d", (value / 1000000), ((value / 1000) % 1000), (value % 1000));
  return ERROR_NONE;
}

int GoPiGo3::get_id(char *str){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_GET_ID;
  // assign error to the value returned by spi_read_32, and if not 0:
  if(int error = spi_transfer_array(20, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  for(int i = 0; i < 16; i++){
    sprintf((str + (i * 2)), "%02X", spi_array_in[i + 4]);
  }
  return ERROR_NONE;
}


bool GoPiGo3::check_serial_number_for_16_ticks(std::string serial_file_path){

    // Returns true if GoPiGo3 serial is in file "/home/pi/Dexter/.list_of_serial_numbers.pkl"
    char serial[33] = "00000000000000000000000000000000";
    get_id(serial);
    std::string serials;

    // Read serials file into string
    std::ifstream file(serial_file_path);
    if(file.is_open()) {
        std::stringstream buffer;
        buffer << file.rdbuf();
        serials = buffer.str();
    }

    bool key_found = (serials.find(serial) != std::string::npos);
    return key_found;
}

int GoPiGo3::load_robot_constants(std::string config_file_path){
    /*
        Load wheel diameter and wheel base width constants for the GoPiGo3 from file.
        This method gets called by the constructor.
        :param string config_file_path = "/home/pi/Dexter/gpg3_config.json": Path to JSON config file that stores the wheel diameter and wheel base width for the GoPiGo3.

        Here's how the JSON config file must look like before reading it. The supported format is JSON so that anyone can
        edit their own config file if they don't want to go through saving the values by using the API.
        .. code-block:: json
            {
                "wheel-diameter": 66.5,
                "wheel-base-width": 117,
                "ticks": 6,
                "motor_gear_ratio": 120
            }
        If the file doesn't exist, one gets written for the user.
        If the file is empty, the file will be overwritten with appropriate default values.
        If the file has content, the robot constants are redefined based on that content. 
        If the tick and gear_ratio are missing, default values will be supplied based on the serial number of the GoPiGo3
    */



    // Load GoPiGo3 constants from /home/pi/Dexter/gpg3_config.json if exists
    // otherwise sets default constants based on presence of serial in /home/pi/Dexter/.list_of_serial_numbers.pkl file

    std::string keys[4] = {"wheel-diameter", "wheel-base-width", "ticks", "motor_gear_ratio"};

    // create a JSON string object from the file
    //    /home/pi/Dexter/gpg3_config.json
    //    {"wheel-diameter": 66.1, "wheel-base-width": 105.59, "ticks": 16, "motor_gear_ratio": 120}
    std::string gpg3_config;
    std::ifstream input(config_file_path);
    std::stringstream buffer;
    input >> buffer.rdbuf();
    gpg3_config = buffer.str();

    // replace a occurances of close-brace with comma to make value extraction consistent for last key:value
    replace(gpg3_config.begin(), gpg3_config.end(), '}', ',');

    // count elements
    auto n_keys = count(gpg3_config.cbegin(), gpg3_config.cend(), ':');

    std::string value_string;
    // test if key found in string
    for (auto &&key: keys){
        auto pos_key = gpg3_config.find(key);
        if (pos_key != std::string::npos){
            auto key_string = gpg3_config.substr(pos_key);
            auto pos_colon = key_string.find(':');
            value_string = key_string.substr(pos_colon+1);
            auto pos_comma = value_string.find(',');
            value_string = value_string.substr(0, pos_comma);
            // std::cout << key << ": value_string: " << '"'+value_string+'"' << std::endl;
        }
        if (key == keys[0]) { // "wheel-diameter":
            if (pos_key == std::string::npos)
              WHEEL_DIAMETER = 66.500;
            else
              WHEEL_DIAMETER = stof(value_string);
        }
        else if (key == keys[1]) {  // "wheel-base-width"
            if (pos_key == std::string::npos)
              WHEEL_BASE_WIDTH = 117.000;
            else
              WHEEL_BASE_WIDTH = stof(value_string);
        }
        else if (key == keys[2]) { // "ticks"
            if (pos_key == std::string::npos) {

                if (check_serial_number_for_16_ticks()){
                    ENCODER_TICKS_PER_ROTATION = 16;
                }
                else {
                    ENCODER_TICKS_PER_ROTATION = 6;
                }
            }

            else
              ENCODER_TICKS_PER_ROTATION = stoi(value_string);
        }
        else if (key == keys[3]) { //"motor_gear_ratio"
            if (pos_key == std::string::npos)
              MOTOR_GEAR_RATIO = 120;
            else
              MOTOR_GEAR_RATIO = stoi(value_string);
        }

    }  // end for

    WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * M_PI;
    WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * M_PI;
    MOTOR_TICKS_PER_DEGREE = ((MOTOR_GEAR_RATIO * ENCODER_TICKS_PER_ROTATION) / 360.0);

    // If the file was not present, or did not contain all four robot constants, write new robot constants file
    if (n_keys < 4) save_robot_constants();
    return ERROR_NONE;
}


int GoPiGo3::save_robot_constants(std::string config_file_path){
    /*
        Write wheel diameter, wheel base width, ticks, motor gear ratio constants to JSON config file

        :param string config_file_path = "/home/pi/Dexter/gpg3_config.json": Path to JSON config file.

        The JSON config file written will look like like this:
        .. code-block:: json
            {
                "wheel-diameter": 66.5,
                "wheel-base-width": 117,
                "ticks": 6,
                "motor_gear_ratio": 120
            }
    */

    std::string keys[4] = {"wheel-diameter", "wheel-base-width", "ticks", "motor_gear_ratio"};

    // create a JSON string object from the keys and "constants"
    //    /home/pi/Dexter/gpg3_config.json
    //    {"wheel-diameter": 66.1, "wheel-base-width": 105.59, "ticks": 16, "motor_gear_ratio": 120}
    std::ostringstream gpg3_config;

    gpg3_config << "{";
    gpg3_config << "\"" << keys[0] << "\"" << ": " << std::fixed << std::setprecision(3) << WHEEL_DIAMETER << ", " ;
    gpg3_config << "\"" << keys[1] << "\"" << ": " << std::fixed << std::setprecision(3) << WHEEL_BASE_WIDTH << ", " ;
    gpg3_config << "\"" << keys[2] << "\"" << ": " << ENCODER_TICKS_PER_ROTATION << ", " ;
    gpg3_config << "\"" << keys[3] << "\"" << ": " << MOTOR_GEAR_RATIO << "}" ;

    // std::cout << "gpg3_config: " << gpg3_config.str() << std::endl;

    std::ofstream outfile(config_file_path);
    outfile << gpg3_config.str();
    // std::cout << config_file_path << " written" << std::endl;

    return ERROR_NONE;
}


int GoPiGo3::set_robot_constants(float wheel_diameter, float wheel_base_width, int ticks, int motor_gear_ratio){

    /*
        Set new values for the GoPiGo3 "robot constants".
        :param float wheel_diameter: Diameter of the GoPiGo3 wheels as measured in millimeters.
        :param float wheel_base_width: The distance between the 2 centers of the 2 wheels as measured in millimeters.
        :param int   ticks:  Number of magnetic pole reversals in one rotation of the motor encoder disk
        :param int   motor_gear_ratio:  Revolutions of motor shaft for each revolution of the wheel shaft

        These values need to be determined when the GoPiGo3's trajectory is skewed due to minor differences between physical and effective measurements.

        The GoPiGo3 class instantiates itself with default values for both constants:
        1. ``wheel_diameter`` is by-default set to **66.5** *mm*.
        2. ``wheel_base_width`` is by-default set to **117** *mm*.
        3. ``ticks`` is by default set to **6**, with GoPiGos manufactured in 2021 using 16.
        4. ``motor_gear_ratio`` is by default set to **120**.
    */
        WHEEL_DIAMETER = wheel_diameter;
        WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * M_PI;
        WHEEL_BASE_WIDTH = wheel_base_width;
        WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * M_PI;
        MOTOR_GEAR_RATIO = motor_gear_ratio;
        ENCODER_TICKS_PER_ROTATION = ticks;
        MOTOR_TICKS_PER_DEGREE = ((MOTOR_GEAR_RATIO * ENCODER_TICKS_PER_ROTATION) / 360.0);

        return ERROR_NONE;

}


int GoPiGo3::set_led(uint8_t led, uint8_t red, uint8_t green, uint8_t blue){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_LED;
  spi_array_out[2] = led;
  spi_array_out[3] = red;
  spi_array_out[4] = green;
  spi_array_out[5] = blue;
  return spi_transfer_array(6, spi_array_out, spi_array_in);
}

float GoPiGo3::get_voltage_5v(){
  float voltage;
  int res = get_voltage_5v(voltage);
  if(res)return res;
  return voltage;
}

int GoPiGo3::get_voltage_5v(float &voltage){
  uint16_t value;
  int res = spi_read_16(GPGSPI_MESSAGE_GET_VOLTAGE_5V, value);
  voltage = value / 1000.0;
  return res;
}

float GoPiGo3::get_voltage_battery(){
  float voltage;
  int res = get_voltage_battery(voltage);
  if(res)return res;
  return voltage;
}

int GoPiGo3::get_voltage_battery(float &voltage){
  uint16_t value;
  int res = spi_read_16(GPGSPI_MESSAGE_GET_VOLTAGE_VCC, value);
  voltage = value / 1000.0;
  return res;
}

int GoPiGo3::set_servo(uint8_t servo, uint16_t us){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_SERVO;
  spi_array_out[2] = servo;
  spi_array_out[3] = ((us >> 8) & 0xFF);
  spi_array_out[4] = (us & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

int GoPiGo3::set_motor_power(uint8_t port, int8_t power){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_PWM;
  spi_array_out[2] = port;
  spi_array_out[3] = power;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

int GoPiGo3::set_motor_position(uint8_t port, int32_t position){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_POSITION;
  spi_array_out[2] = port;
  spi_array_out[3] = ((position >> 24) & 0xFF);
  spi_array_out[4] = ((position >> 16) & 0xFF);
  spi_array_out[5] = ((position >> 8) & 0xFF);
  spi_array_out[6] = (position & 0xFF);
  return spi_transfer_array(7, spi_array_out, spi_array_in);
}

int GoPiGo3::set_motor_dps(uint8_t port, int16_t dps){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_DPS;
  spi_array_out[2] = port;
  spi_array_out[3] = ((dps >> 8) & 0xFF);
  spi_array_out[4] = (dps & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

int GoPiGo3::set_motor_limits(uint8_t port, uint8_t power, uint16_t dps){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_LIMITS;
  spi_array_out[2] = port;
  spi_array_out[3] = power;
  spi_array_out[4] = ((dps >> 8) & 0xFF);
  spi_array_out[5] = (dps & 0xFF);
  return spi_transfer_array(6, spi_array_out, spi_array_in);
}

int GoPiGo3::get_motor_status(uint8_t port, uint8_t &state, int8_t &power, int32_t &position, int16_t &dps){
  uint8_t msg_type;
  switch(port){
    case MOTOR_LEFT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_STATUS_LEFT;
    break;
    case MOTOR_RIGHT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_STATUS_RIGHT;
    break;
    default:
      fatal_error("get_motor_status error. Must be one motor at a time. MOTOR_LEFT or MOTOR_RIGHT.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(12, spi_array_out, spi_array_in)){
    return error;
  }

  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }

  state    = spi_array_in[4];
  power    = spi_array_in[5];
  position = ((spi_array_in[6] << 24) | (spi_array_in[7] << 16) | (spi_array_in[8] << 8) | spi_array_in[9]);
  dps      = ((spi_array_in[10] << 8) | spi_array_in[11]);

  return ERROR_NONE;
}

int GoPiGo3::offset_motor_encoder(uint8_t port, int32_t position){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_OFFSET_MOTOR_ENCODER;
  spi_array_out[2] = port;
  spi_array_out[3] = ((position >> 24) & 0xFF);
  spi_array_out[4] = ((position >> 16) & 0xFF);
  spi_array_out[5] = ((position >> 8) & 0xFF);
  spi_array_out[6] = (position & 0xFF);
  return spi_transfer_array(7, spi_array_out, spi_array_in);
}

int32_t GoPiGo3::get_motor_encoder(uint8_t port){
  int32_t value;
  get_motor_encoder(port, value);
  return value;
}

int GoPiGo3::reset_motor_encoder(uint8_t port){
  if (port & MOTOR_LEFT){
    offset_motor_encoder(MOTOR_LEFT, get_motor_encoder(MOTOR_LEFT));
  }
  if (port & MOTOR_RIGHT){
    offset_motor_encoder(MOTOR_RIGHT, get_motor_encoder(MOTOR_RIGHT));
  }
  return ERROR_NONE;
}


int GoPiGo3::get_motor_encoder(uint8_t port, int32_t &value){
  uint8_t msg_type;
  switch(port){
    case MOTOR_LEFT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_ENCODER_LEFT;
    break;
    case MOTOR_RIGHT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_ENCODER_RIGHT;
    break;
    default:
      fatal_error("get_motor_encoder error. Must be one motor at a time. MOTOR_LEFT or MOTOR_RIGHT.");
  }
  uint32_t Value;
  int res = spi_read_32(msg_type, Value);
  value = Value;
  return res;
}

int GoPiGo3::set_grove_type(uint8_t port, uint8_t type){
  if((port & GROVE_1) == GROVE_1){
    GroveType[0] = type;
  }
  if((port & GROVE_2) == GROVE_2){
    GroveType[1] = type;
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_TYPE;
  spi_array_out[2] = port;
  spi_array_out[3] = type;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

int GoPiGo3::set_grove_mode(uint8_t pin, uint8_t mode){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_MODE;
  spi_array_out[2] = pin;
  spi_array_out[3] = mode;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

int GoPiGo3::set_grove_state(uint8_t pin, uint8_t state){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_STATE;
  spi_array_out[2] = pin;
  spi_array_out[3] = state;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

int GoPiGo3::set_grove_pwm_duty(uint8_t pin, float duty){
  if(duty > 100){
    duty = 100;
  }else if(duty < 0){
    duty = 0;
  }
  uint16_t duty_value = duty * 10;
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_PWM_DUTY;
  spi_array_out[2] = pin;
  spi_array_out[3] = ((duty_value >> 8) & 0xFF);
  spi_array_out[4] = (duty_value & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

int GoPiGo3::set_grove_pwm_frequency(uint8_t port, uint16_t freq){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_PWM_FREQUENCY;
  spi_array_out[2] = port;
  spi_array_out[3] = ((freq >> 8) & 0xFF);
  spi_array_out[4] = (freq & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

int GoPiGo3::grove_i2c_transfer(uint8_t port, i2c_struct_t *i2c_struct){
  double Timeout = get_time() + 0.005;
  bool Continue = false;
  int error;
  while(!Continue){
    if(error = grove_i2c_start(port, i2c_struct)){
      if(get_time() >= Timeout){
        return error;
      }
    }else{
      Continue = true;
    }
  }

  double DelayTime = 0;
  if(i2c_struct->length_write){
    DelayTime += 1 + i2c_struct->length_write;
  }
  if(i2c_struct->length_read){
    DelayTime += 1 + i2c_struct->length_read;
  }
  DelayTime *= 0.000115;         // each I2C byte takes about 115uS at full speed (about 100kbps)
  // No point trying to read the values before they are ready.
  usleep((DelayTime * 1000000)); // delay for as long as it will take to do the I2C transaction.
  Timeout = get_time() + 0.005;  // timeout after 5ms of failed attempted reads

  while(true){
    if(error = get_grove_value(port, i2c_struct)){
      if(get_time() >= Timeout){
        return error;
      }
    }else{
      return ERROR_NONE;
    }
  }
}

int GoPiGo3::grove_i2c_start(uint8_t port, i2c_struct_t *i2c_struct){
  uint8_t msg_type;
  uint8_t port_index;
  switch(port){
    case GROVE_1:
      msg_type = GPGSPI_MESSAGE_START_GROVE_I2C_1;
      port_index = 0;
    break;
    case GROVE_2:
      msg_type = GPGSPI_MESSAGE_START_GROVE_I2C_2;
      port_index = 1;
    break;
    default:
      fatal_error("grove_i2c_start error. Must be one grove port at a time. GROVE_1 or GROVE_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  spi_array_out[2] = ((i2c_struct->address & 0x7F) << 1);

  if(i2c_struct->length_read > LONGEST_I2C_TRANSFER){
    i2c_struct->length_read = LONGEST_I2C_TRANSFER;
  }
  spi_array_out[3] = i2c_struct->length_read;
  GroveI2CInBytes[port_index] = i2c_struct->length_read;

  if(i2c_struct->length_write > LONGEST_I2C_TRANSFER){
    i2c_struct->length_write = LONGEST_I2C_TRANSFER;
  }
  spi_array_out[4] = i2c_struct->length_write;

  for(uint8_t i = 0; i < i2c_struct->length_write; i++){
    spi_array_out[5 + i] = i2c_struct->buffer_write[i];
  }

  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array((5 + i2c_struct->length_write), spi_array_out, spi_array_in)){
    return error;
  }

  // If the fourth byte received is not 0xA5
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  // If the fifth byte received is not GROVE_STATUS_VALID_DATA
  if(spi_array_in[4] != GROVE_STATUS_VALID_DATA){
    return spi_array_in[4];
  }

  return ERROR_NONE;
}

int GoPiGo3::get_grove_value(uint8_t port, void *value_ptr){
  uint8_t msg_type;
  uint8_t port_index;
  switch(port){
    case GROVE_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VALUE_1;
      port_index = 0;
    break;
    case GROVE_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VALUE_2;
      port_index = 1;
    break;
    default:
      fatal_error("get_grove_value error. Must be one grove port at a time. GROVE_1 or GROVE_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;

  uint8_t spi_transfer_length;

  // Determine the SPI transaction byte length based on the grove type
  switch(GroveType[port_index]){
    case GROVE_TYPE_IR_DI_REMOTE:
      spi_transfer_length = 7;
    break;
    case GROVE_TYPE_IR_EV3_REMOTE:
      spi_transfer_length = 10;
    break;
    case GROVE_TYPE_US:
      spi_transfer_length = 8;
    break;
    case GROVE_TYPE_I2C:
      spi_transfer_length = 6 + GroveI2CInBytes[port_index];
    break;
    default:
      return GROVE_STATUS_NOT_CONFIGURED;
    break;
  }

  // Get the grove value(s), and if error
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(spi_transfer_length, spi_array_out, spi_array_in)){
    return error;
  }
  // If the fourth byte received is not 0xA5
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  // If the grove type is not what it should be
  if(spi_array_in[4] != GroveType[port_index]){
    printf("get_grove_value %d != %d for port index %d\n", spi_array_in[4], GroveType[port_index], port_index);
    return ERROR_GROVE_TYPE_MISMATCH;
  }
  // If the sensor value(s) is not valid (still configuring the grove port, or error communicating with grove device)
  if(spi_array_in[5] != GROVE_STATUS_VALID_DATA){
    return spi_array_in[5];
  }

  if(GroveType[port_index] == GROVE_TYPE_IR_DI_REMOTE){
    sensor_infrared_gobox_t *Value = (sensor_infrared_gobox_t*)value_ptr;
    Value->button = spi_array_in[6];
  }else if(GroveType[port_index] == GROVE_TYPE_IR_EV3_REMOTE){
    sensor_infrared_ev3_t *Value = (sensor_infrared_ev3_t*)value_ptr;
    Value->remote[0] = spi_array_in[6];
    Value->remote[1] = spi_array_in[7];
    Value->remote[2] = spi_array_in[8];
    Value->remote[3] = spi_array_in[9];
  }else if(GroveType[port_index] == GROVE_TYPE_US){
    sensor_ultrasonic_t *Value = (sensor_ultrasonic_t*)value_ptr;
    Value->mm = (((spi_array_in[6] << 8) & 0xFF00) | (spi_array_in[7] & 0xFF));
    Value->cm = Value->mm / 10.0;
    Value->inch = Value->mm / 25.4;
  }else if(GroveType[port_index] == GROVE_TYPE_I2C){
    i2c_struct_t *Value = (i2c_struct_t*)value_ptr;
    for(uint8_t b = 0; b < GroveI2CInBytes[port_index]; b++){
      Value->buffer_read[b] = spi_array_in[6 + b];
    }
  }
  return GROVE_STATUS_VALID_DATA;
}

uint8_t GoPiGo3::get_grove_state(uint8_t pin){
  uint8_t value;
  get_grove_state(pin, value);
  return value;
}

int GoPiGo3::get_grove_state(uint8_t pin, uint8_t &value){
  value = 0;
  uint8_t msg_type;
  switch(pin){
    case GROVE_1_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_1_1;
    break;
    case GROVE_1_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_1_2;
    break;
    case GROVE_2_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_2_1;
    break;
    case GROVE_2_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_2_2;
    break;
    default:
      fatal_error("get_grove_state error. Must be one pin at a time. GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(6, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] == 0xA5){
    if(spi_array_in[4] == GROVE_STATUS_VALID_DATA){
      value = spi_array_in[5];
      return ERROR_NONE;
    }else{
      return ERROR_GROVE_DATA_ERROR;
    }
  }else{
    return ERROR_SPI_RESPONSE;
  }
}

float GoPiGo3::get_grove_voltage(uint8_t pin){
  float value;
  get_grove_voltage(pin, value);
  return value;
}

int GoPiGo3::get_grove_voltage(uint8_t pin, float &value){
  value = 0;
  uint8_t msg_type;
  switch(pin){
    case GROVE_1_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_1;
    break;
    case GROVE_1_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_2;
    break;
    case GROVE_2_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_1;
    break;
    case GROVE_2_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_2;
    break;
    default:
      fatal_error("get_grove_voltage error. Must be one pin at a time. GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(7, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] == 0xA5){
    if(spi_array_in[4] == GROVE_STATUS_VALID_DATA){
      value = (((spi_array_in[5] << 8) & 0xFF) | (spi_array_in[5] & 0xFF)) / 1000.0;
      return ERROR_NONE;
    }else{
      return ERROR_GROVE_DATA_ERROR;
    }
  }else{
    return ERROR_SPI_RESPONSE;
  }
}

uint16_t GoPiGo3::get_grove_analog(uint8_t pin){
  uint16_t value;
  get_grove_analog(pin, value);
  return value;
}

int GoPiGo3::get_grove_analog(uint8_t pin, uint16_t &value){
  value = 0;
  uint8_t msg_type;
  switch(pin){
    case GROVE_1_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_1;
    break;
    case GROVE_1_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_2;
    break;
    case GROVE_2_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_1;
    break;
    case GROVE_2_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_2;
    break;
    default:
      fatal_error("get_grove_analog error. Must be one pin at a time. GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(7, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] == 0xA5){
    if(spi_array_in[4] == GROVE_STATUS_VALID_DATA){
      value = (((spi_array_in[5] << 8) & 0xFF) | (spi_array_in[5] & 0xFF));
      return ERROR_NONE;
    }else{
      return ERROR_GROVE_DATA_ERROR;
    }
  }else{
    return ERROR_SPI_RESPONSE;
  }
}

int GoPiGo3::reset_all(){
  int res1 = set_grove_type(GROVE_1 + GROVE_2, GROVE_TYPE_CUSTOM);
  int res2 = set_motor_power(MOTOR_LEFT + MOTOR_RIGHT, MOTOR_FLOAT);
  int res3 = set_motor_limits(MOTOR_LEFT + MOTOR_RIGHT, 0, 0);
  int res4 = set_led((LED_EYE_LEFT + LED_EYE_RIGHT + LED_BLINKER_LEFT + LED_BLINKER_RIGHT), 0, 0, 0);
  int res5 = set_grove_pwm_duty(GROVE_1 + GROVE_2, 0);
  int res6 = set_grove_pwm_frequency(GROVE_1 + GROVE_2);
  if(res1){
    return res1;
  }else if(res2){
    return res2;
  }else if(res3){
    return res3;
  }else if(res4){
    return res4;
  }else if(res5){
    return res5;
  }else if(res6){
    return res6;
  }
  return ERROR_NONE;
}
