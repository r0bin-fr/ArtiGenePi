import readBT
import multithreadBT
import multithreadServeur
import SSRControl
import time
import sys
import signal
import gaugette.rotary_encoder as RE
import gaugette.gpio as GG

from WRX_HUD.Hardware.SH1106.SH1106LCD import *
from WRX_HUD.Hardware.I2CConfig import *
from WRX_HUD.Hardware.SH1106.SH1106FontLib import *

# global values for data handling
maximT = readBT.BTData(0)
taskT = multithreadBT.TaskPrintTemp(maximT)
taskS = multithreadServeur.TaskServeur(maximT)
done = False

#encoder data
powval = 50
A_PIN = 25
B_PIN = 24

#how to quit application nicely
def quitApplicationNicely():
	done = True
	taskS.stop()
	taskT.stop()
	SSRControl.setBoilerPWM(0)
	time.sleep(0.1)
        sys.exit(0)

#signal handler
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
	quitApplicationNicely()

#intercept control c for nice quit
signal.signal(signal.SIGINT, signal_handler)

#start tasks
taskT.start()
taskS.start()

#encoder settings
gpio = GG.GPIO()
encoder = RE.RotaryEncoder(gpio, A_PIN, B_PIN,0)
encoder.start()

#OLED screen
i2cConfig()
lcd = SH1106LCD()
lcd.clearScreen()
lcd.displayInvertedString("----- ArtiGene ------", 0, 0)

def refreshScreen():

	tc,tmi,tma,bat = maximT.getAllData()
	lcd.displayString("Temp="+str(tc)+"C   ",	1,0)
	lcd.displayString("TempMin="+str(tmi)+"C   ",	2,0)
	lcd.displayString("TempMax="+str(tma)+"C   ",	3,0)
	lcd.displayString("Batt="+str(bat)+"%   ",	4,0)
	lcd.displayString("Power="+str(powval)+"%   ",	5,0)

# -------- Main Program: check encoder settings  -----------
while True:
	#encoder read
	delta = encoder.get_steps()
	#did we turn the encoder?
      	if delta!=0:
		#compute new power value
        	#print "rotate %d" % delta
        	powval = powval + (2 * delta)
        	if powval > 100:
                	powval = 100
        	if powval < 0:
                	powval = 0
        	print "New power value= %d" % powval
		#update PWM to SSR
		SSRControl.setBoilerPWM(powval)		
      	else:
		refreshScreen()
        	time.sleep(0.1)



