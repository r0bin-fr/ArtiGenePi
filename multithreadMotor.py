import os
import glob
import time
import threading
import binascii
import struct
import time
import sys
import readBT
import SSRControl

class TaskRunMotor(threading.Thread): 

    def __init__(self): #, mData = readBT.BTData()): 
        threading.Thread.__init__(self) 
        self._stopevent = threading.Event( ) 
	#self.lok = threading.Lock()
	#self.mData = mData
	

    #main task body
    def run(self):
	#reduce speed to allow temp reading
	setMotorPWM(30)
	#wait 4 seconds
	self._stopevent.wait(4)
	#now run full speed until next time!
	setMotorPWM(100)


    def stop(self): 
	print "stopping thread Motor"
        self._stopevent.set( ) 


#control PWM motor
def setMotorPWM(drive,doinit=0):
	print "setMotorPWM to :",drive
	SSRControl.setMotorPWM(drive,doinit)

