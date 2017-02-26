#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define PWCLKDIVIDER	2400
#define PWRANGE  	4000

/*****************************************
 * WiringPi launcher to set PWM          *
 * based on James Ward PWM settings      *
 * to work with SSR and Espresso machine *
 *****************************************/
int main (int argc, char *argv[])
{
  int drive = 0;
  int reto = 0;

  if(argc != 2)
  {
	printf("Error: invalid arguments. Usage: sudo pwmlauncher <aaa> where aaa is the drive percent\n");
	exit(0); 
  }
  //printf ("Welcome into PWM drive launcher\n") ;
  //retrieve argument
  drive = atoi(argv[1]);
  if(drive > 100)
    drive = 100;
  printf("drive=%d%\n",drive);

  //init wiringpi
  if (wiringPiSetupGpio() == -1){
    printf("Error inint wiringpi lib\n");
    exit (1) ;
  }

  //PWM mode
  pinMode(18,PWM_OUTPUT);
  //PWM "predictive mode"
  pwmSetMode(PWM_MODE_MS); 

  //set clock at 2Hz (clock divider / range)
  pwmSetClock(PWCLKDIVIDER);
  pwmSetRange (PWRANGE) ;
  //setting drive according to the RANGE 
  pwmWrite (18, (drive * (PWRANGE / 100))); 
}
