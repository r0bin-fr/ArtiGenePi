import os
import glob
import time
import threading
import sys
import subprocess
from RPi import GPIO

# pin=13 frequency=8Hz
HEATER_GPIO = 13
PWM_FREQUENCY = 8.333

#class to handle PWM functions
class MyPWM:
	#init vars
	def __init__(self):
		self.pwmHeater = 0

	#use RPi.GPIO library to handle non-critical software PWM
	def setHeaterPWM(self,drive=0, doinit=0):
		#should be called only once
		if doinit or (self.pwmHeater == 0):
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(13, GPIO.OUT)
			self.pwmHeater = GPIO.PWM(HEATER_GPIO, PWM_FREQUENCY)
			self.pwmHeater.start(0)
		#update pwm drive
		self.pwmHeater.ChangeDutyCycle(drive)		

	# commenting because causing incompatibility with motor PWM
	#	try:
	#        	task = subprocess.Popen(['sudo','/home/pi/roasterpy/pwmlauncher',str(doinit),str(drive)])
	#		task_result = task.returncode
	#        except:
	#		print "Wiring pi error"


#call a C program using WiringPi to control PWM
def setMotorPWM(drive=0, doinit=0):
        try:
                task = subprocess.Popen(['sudo','/home/pi/roasterpy/pwmlauncherMotor',str(doinit),str(drive)])
                task_result = task.returncode
        except:
                print "Wiring pi error"

