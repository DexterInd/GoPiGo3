/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  LED Display Program for C++
 */
#include <iostream>
#include <GoPiGo3.h>
#include <termios.h>
#include <unistd.h>

using namespace std;

//Check for a keyboard hit (but ENTER must be pressed, also
int kbhit()
{
    struct timeval tv;
    fd_set fds;
    tv.tv_sec = 0;
    tv.tv_usec = 0;
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds); //STDIN_FILENO is 0
    select(STDIN_FILENO+1, &fds, NULL, NULL, &tv);
    return FD_ISSET(STDIN_FILENO, &fds);
}

int main()
{
  cout << "Starting LED Display" << endl;
  cout << "Ironically, click on ENTER to exit the application" << endl;
  GoPiGo3 *gpg = new GoPiGo3();
  gpg->reset_all();  //Reset everything.

  try
  {
    //Continue until enter is hit.
    while (!kbhit())
    {
      for (int ndx = 0; ndx < 11; ++ndx)
      {
        gpg->set_led(LED_EYE_LEFT, ndx, ndx, ndx);   //set the LED brightness (0 to 255)
        gpg->set_led(LED_EYE_RIGHT, 10 - ndx, 10 - ndx, 10 - ndx);   //set the LED brightness (255 to 0)
        gpg->set_led(LED_BLINKER_LEFT, (ndx * 25));           // set the LED brightness (0 to 255)
        gpg->set_led(LED_BLINKER_RIGHT, ((10 - ndx) * 25));     // set the LED brightness (255 to 0)
        usleep(20000);                               // delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.
      }

      gpg->set_led(LED_WIFI, 0, 0, 10);

      for (int ndx = 0; ndx < 11; ++ndx)         // count from 0-10
      {
        gpg->set_led(LED_EYE_LEFT, 10 - ndx, 10 - ndx, 10 - ndx);  // set the LED brightness (255 to 0)
        gpg->set_led(LED_EYE_RIGHT, ndx, ndx, ndx);                // set the LED brightness (0 to 255)
        gpg->set_led(LED_BLINKER_LEFT, ((10 - ndx) * 25));     // set the LED brightness (0 to 255)
        gpg->set_led(LED_BLINKER_RIGHT, (ndx * 25));           // set the LED brightness (255 to 0)
        usleep(20000);                              // delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.
      }
      gpg->set_led(LED_WIFI, 0, 0, 0);
    }
  }
  catch(...)
  {
    cout << "Error!" << endl;
  }
  gpg->reset_all(); // Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
  delete gpg;
  return 0;
}
