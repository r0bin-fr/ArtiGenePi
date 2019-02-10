import readBT
import multithreadBT
import multithreadServeur
import multithreadMotor
import SSRControl
import time
import sys
import signal
import gaugette.rotary_encoder as RE
#import gaugette.gpio as GG
import RPi.GPIO as GPIO
import myencoder
import myplotly
import readMaximSPI

from WRX_HUD.Hardware.SH1106.SH1106LCD import *
from WRX_HUD.Hardware.I2CConfig import *
from WRX_HUD.Hardware.SH1106.SH1106FontLib import *

# global values for data handling
maximT = readBT.BTData(0)
myTempSensor = readMaximSPI.MaximSPI()

taskT = multithreadBT.TaskPrintTemp(maximT)
taskS = multithreadServeur.TaskServeur(maximT,myTempSensor)
done = False
isRoasterNotStarted = True

#plotly data
myplot = myplotly.MyPlotly(1)

#for PWM/SSR
myHeater = SSRControl.MyPWM()

#motor data
IN1_PIN = 17
IN2_PIN = 27
isMotorControl = 1

#encoder data
powval = 50
A_PIN = 26#25
B_PIN = 19#24
SW_PIN = 22

#how to quit application nicely
def quitApplicationNicely():
	done = True
	taskS.stop()
	taskT.stop()
	myplot.closeStream()
#	encoder.stop()
	myHeater.setHeaterPWM(0)
	multithreadMotor.setMotorPWM(100)
	lcd.clearScreen()
	time.sleep(0.1)
	print "now exit"
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
encoder = myencoder.RotaryEncoder( A_PIN, B_PIN,SW_PIN )
encoder.start()

#OLED screen
i2cConfig()
lcd = SH1106LCD()
lcd.clearScreen()
lcd.displayInvertedString("----- ArtiGene ------", 0, 0)

#OLED paint func
def refreshScreen():
	global isMotorControl,isRoasterNotStarted
#	print "rs1"
	tc,tmi,tma,bat = maximT.getAllData()
	az = maximT.getAccelZ()
	mp = maximT.getMotorP()
	tmi2 = maximT.getAccelX()
	tma2 = maximT.getAccelY()
#	print "rs2"
	#lcd.displayString("TTemp="+str(tc)+"C   ",	1,0)
	if(taskT.isBTNOK):
		lcd.displayString("                     ",1,0)
		lcd.displayString("   BT DISCONNECTED   ",2,0)
		lcd.displayString("                     ",3,0)
	else:
		lcd.displayString("TMin="+str(tmi)+" - "+str(tmi2)+"   ",	1,0)
		lcd.displayString("TMax="+str(tma)+" - "+str(tma2)+"   ",	2,0)
		lcd.displayString("Batt="+str(bat)+"%   ",			3,0)
#	print "rs3"
	lcd.displayString("Heater="+str(powval)+"/12   ",	4,0)
	myTempSensor.read_temp()
	myProbeTemp = myTempSensor.getTemp()
	lcd.displayString("Probe temp="+ str(myProbeTemp) +"C   ",5,0)
	if(isMotorControl == 0):
		lcd.displayInvertedString(" Motor=OFF             ",7,0)
	if(isMotorControl == 1):
		lcd.displayInvertedString(" Motor=ON Control=OFF ",7,0)		
	if(isMotorControl == 2):
		lcd.displayInvertedString(" Motor=ON Control=ON  ",7,0)
#	print "rs4"

	#udpate plotly only when roast is started
	if(isRoasterNotStarted == False):
		if(taskT.isBTNOK):
			#if BT is disconnected, only update loval vals
			myplot.update(0, 0, 0, myProbeTemp, powval, 0)		
		else:
			myplot.update(tc, tmi, tma, myProbeTemp, powval, az)
#	print "rs5"


#L293D init
def initMotorDrive():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(IN1_PIN, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(IN2_PIN, GPIO.OUT, initial=GPIO.HIGH)
#switch motor side
def setMotorSens(sens):
	if(sens == 1):
		GPIO.output(IN1_PIN,GPIO.LOW)
		GPIO.output(IN2_PIN,GPIO.HIGH)
	else:
		GPIO.output(IN1_PIN,GPIO.HIGH)
		GPIO.output(IN2_PIN,GPIO.LOW)

#motor control vars		
momax = 100
momin = -100
mostep = 30
mosens = 1
motval = 100
#heater control vars
powval = 12
hemax = 12
hemin = 0

def main_controlHeater():
	global powval,isMotorControl,isRoasterNotStarted
	#did we push the button?
	if(encoder.get_bPushed() == True):
		isMotorControl = isMotorControl+1
		if(isMotorControl >= 3):
			isMotorControl = 0
		#update BT thread
		taskT.setMotorControl(isMotorControl)
		
	#encoder read
	delta = encoder.get_cycles() #get_steps()
	#did we turn the encoder?
	if delta!=0:
		#compute new power value
       		powval = powval + delta
        	if powval > hemax:
                	powval = hemax
        	if powval < hemin:
                	powval = hemin
        	print "New power value= %d" % powval
		#translate to percent
		ppercent = (powval * 100) / hemax
		#update PWM to SSR
		myHeater.setHeaterPWM(ppercent,0)
		#update shared memory
		maximT.setHeaterP(powval)		
      	else:
		#initiate roast when first BT connection detected
		if((taskT.isBTNOK == 0) and (isRoasterNotStarted)):
			myplot.initTimeStamp()
			isRoasterNotStarted = False
		refreshScreen()
        	time.sleep(0.1)

# -------- Main Program: check encoder settings  -----------
initMotorDrive()
SSRControl
multithreadMotor.setMotorPWM(100,1)
myHeater.setHeaterPWM(100,1)

while True:
	main_controlHeater()
	#main_controlMotor()


#old func for test only
def main_controlMotor():
        #encoder read
        delta = encoder.get_cycles() #get_steps()
        #did we turn the encoder?
        if delta!=0:
                #compute new power value
                motval = motval + (delta * mostep)
                if motval > momax:
                        motval = momax
                if motval < momin:
                        motval = momin
                print "New motor value= %d" % motval
                #update PWM to SSR
		maximT.setMotorP(motval)
                SSRControl.setMotorPWM(abs(motval))
		#change de sens
		if(motval < 0) and (mosens == 1):
			mosens = 0
			setMotorSens(mosens)
		if(motval > 0) and (mosens == 0):
                        mosens = 1
                        setMotorSens(mosens)
        else:
                refreshScreen()
                time.sleep(0.1)

