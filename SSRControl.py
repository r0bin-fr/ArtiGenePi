import os
import glob
import time
import threading
import sys
import subprocess

#call a C program using WiringPi to control PWM
def setBoilerPWM(drive=0):
	try:
        	task = subprocess.Popen(['sudo','/home/pi/roasterpy/pwmlauncher',str(drive)])
		task_result = task.returncode
        except:
		print "Wiring pi error"

