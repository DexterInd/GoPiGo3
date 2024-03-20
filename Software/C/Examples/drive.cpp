/*   FILE:  drive.cpp

     PURPOSE:  Demonstrate using GoPiGo3 motors and encoders in C++

     BUILDING:
        Use cmake:
           - cd /home/pi/Dexter/GoPiGo3/Software/C
           - cmake CMakeLists.txt
           - make

     USAGE:
         - /home/pi/Dexter/GoPiGo3/Software/C/drive
           or
         - cd /home/pi/Dexter/GoPiGo3/Software/C
           ./drive

         - press q to quit program (only way, ctrl-c does not exit)
         - press spacebar to stop GoPiGo3
         - press s to spin GoPiGo3
         - press a to rotate around left wheel
         - press d to rotate around right wheel
         - press w to drive forward
         - press x to drive backward
         - press r to reset encoders to 0
*/

#include <GoPiGo3.h>   // for GoPiGo3
#include <stdio.h>     // for printf
#include <unistd.h>    // for usleep
#include <signal.h>    // for catching exit signals


#define NO_LIMIT_SPEED 1000

GoPiGo3 GPG;

void exit_signal_handler(int signo);

int main(){

        int left_enc, right_enc;

	signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C

	GPG.detect();

	printf("\n**** GoPiGo3 Robot Constants:\n");
	printf(" - WHEEL_DIAMETER: %.3f mm\n", GPG.WHEEL_DIAMETER);
	printf(" - WHEEL_BASE_WIDTH: %.3f mm\n", GPG.WHEEL_BASE_WIDTH);
	printf(" - ENCODER_TICKS_PER_ROTATION: %d\n", GPG.ENCODER_TICKS_PER_ROTATION);
	printf(" - MOTOR_GEAR_RATIO: %d\n", GPG.MOTOR_GEAR_RATIO);



	bool keepLooping = true;
        printf("\n****");
	printf("\n        fwd w                  r reset encoders ");
	printf("\n left  a  spin s   d  right");
	printf("\n            bkwd x ");
        printf("\n                               spacebar  STOP");
        printf("\n****");

	GPG.reset_motor_encoder(MOTOR_LEFT + MOTOR_RIGHT);

        // set limits to safe value that will not allow GoPiGo3 to tip over
	GPG.set_motor_limits(MOTOR_LEFT,0,150);
	GPG.set_motor_limits(MOTOR_RIGHT,0,150);

	do{

                printf("\n");
                GPG.get_motor_encoder(MOTOR_LEFT,left_enc);
                GPG.get_motor_encoder(MOTOR_RIGHT,right_enc);

		printf("\nencoders: (%d, %d) Cmd: (q to exit): ",left_enc,right_enc);

		// using stty raw is a terrible idea, not recommended!
		system("stty raw");
		char c = getchar();
                system("stty cooked");

		switch(c){
			case 'w':  // forward
				GPG.set_motor_dps(MOTOR_LEFT + MOTOR_RIGHT, NO_LIMIT_SPEED);
                                // GPG.set_motor_power(MOTOR_LEFT + MOTOR_RIGHT, 10);
				break;
			case 'x' :    // backward
				GPG.set_motor_dps(MOTOR_LEFT + MOTOR_RIGHT, NO_LIMIT_SPEED * -1);
				break;
			case 'd' :    // right turn
				GPG.set_motor_dps(MOTOR_LEFT, NO_LIMIT_SPEED);
				GPG.set_motor_dps(MOTOR_RIGHT, 0);
				break;
			case 'a' :     // left turn
				GPG.set_motor_dps(MOTOR_LEFT, 0);
				GPG.set_motor_dps(MOTOR_RIGHT, NO_LIMIT_SPEED);
				break;
			case 'q' :     // quit
				GPG.set_motor_dps(MOTOR_LEFT + MOTOR_RIGHT, 0);
				keepLooping = false;
				break;
			case ' ' :  // stop
				GPG.set_motor_dps(MOTOR_LEFT + MOTOR_RIGHT, 0);
				std::cout << "stopping..";
				std::cout.flush();
				sleep(1); // wait for stop to finish
				break;
			case 's' :  // spin
				GPG.set_motor_dps(MOTOR_LEFT, (int)(NO_LIMIT_SPEED/2) );
				GPG.set_motor_dps(MOTOR_RIGHT, (int)(-NO_LIMIT_SPEED/2) );
				break;
			case 'r' :  // reset encoders to zero
				GPG.reset_motor_encoder(MOTOR_LEFT + MOTOR_RIGHT);
				break;

		}
	} while (keepLooping);
	system("stty cooked");
        printf("\n");
}


void exit_signal_handler(int signo){
	  if(signo == SIGINT){
         GPG.reset_all();    // Reset everything so there are no run-away motors
         system("stty cooked");
         printf("\n");
         exit(-2);
	  }
}
