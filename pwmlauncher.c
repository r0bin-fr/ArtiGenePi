#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define PWCLKDIVIDER	2400
#define PWRANGE  	1000 //1000 //2000 //4000 = 50 levels, 2000 = 25 levels, 1000 = 12 levels
#define GPIOPINPWM	13//20//13 //13 is software PWM, 18 is hardware PWM but already used

/*****************************************
 * WiringPi launcher to set PWM          *
 * based on James Ward PWM settings      *
 * to work with SSR and Espresso machine *
 *****************************************/
int main (int argc, char *argv[])
{
  int drive = 0;
  int doinit = 0;

  if(argc != 3)
  {
	printf("Error: invalid arguments. Usage: sudo pwmlauncher <a> <bbb> where a is init (1 or 0) and bbb the drive percent\n");
	exit(0); 
  }
  //printf ("Welcome into PWM drive launcher\n") ;
  //retrieve init argument
  doinit = atoi(argv[1]);
  //retrieve drive argument
  drive = atoi(argv[2]);
  if(drive > 100)
    drive = 100;
  printf("heater drive=%d%\n",drive);

  //init wiringpi
	if (wiringPiSetupGpio() == -1){
    		printf("Error inint wiringpi lib\n");
    		exit (1) ;
  	}

  if(doinit){
	printf("init pwm\n");

  	//PWM mode
  	pinMode(GPIOPINPWM,PWM_OUTPUT);
  	//PWM "predictive mode"
  	pwmSetMode(PWM_MODE_MS);

  	//set clock at 2Hz (clock divider / range)
  	pwmSetClock(PWCLKDIVIDER);
  	pwmSetRange (PWRANGE) ;
  }

  //setting drive according to the RANGE
  pwmWrite (GPIOPINPWM, (drive * (PWRANGE / 100)));
}
