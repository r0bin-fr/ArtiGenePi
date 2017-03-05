import os
import glob
import time
import threading
import binascii
import struct
import time
import sys
from bluepy.bluepy.btle import UUID, Peripheral, Characteristic, BTLEException
import readBT


class TaskPrintTemp(threading.Thread): 

    def __init__(self, mData = readBT.BTData()): 
        threading.Thread.__init__(self) 
        self._stopevent = threading.Event( ) 
	self.mData = mData
	self.p = 0
	self.cht = 0
	self.chtmin = 0
	self.chtmax = 0
	self.chb = 0
	self.previousT = time.time()
	self.interval = 0.5
	self.Tlast = self.Tnow = self.Tmax = self.Tmin = 0
 	self.T_dif_now = self.T_dif_last = 0
	self.TminLoopCount = 0
	self.TmaxLoopCount = 0
	self.batt = 0

    def connect(self):
	#UUID where temp is stored
	tempc_uuid = UUID(0x0021)
	tempmin_uuid = UUID(0x0022)
	tempmax_uuid = UUID(0x0023)
	batt_uuid = UUID(0x0024)
	isBTNOK = 1

	#connection...
	while not self._stopevent.isSet() and isBTNOK:
		try:
			print("Connection...")
			#my bluefruit address
			self.p = Peripheral("E9:76:C8:5D:FB:24", "random")

    			print("OK!\ngetCharacteristics")
    			self.cht = self.p.getCharacteristics(uuid=tempc_uuid)[0]
    			self.chtmin = self.p.getCharacteristics(uuid=tempmin_uuid)[0]
    			self.chtmax = self.p.getCharacteristics(uuid=tempmax_uuid)[0]
			self.chb = self.p.getCharacteristics(uuid=batt_uuid)[0]
			isBTNOK = 0

		except BTLEException as e:
			print "CONNECT - BTLEException : {0}".format(e)
			if self.p != 0:
				self.p.disconnect()

		except:
			print 'CONNECT - Other error! ',sys.exc_info()[0]
			if self.p != 0:
				self.p.disconnect()

		#wait 1 second before try again
		if(not self._stopevent.isSet()):
			self._stopevent.wait(1) 

    #extract float data from BLE struct
    def extractBLEval(self,data):
	val = binascii.b2a_hex(data)
        val = binascii.unhexlify(val)
        val = struct.unpack('f', val)[0]
        return float(val)


    def read(self):
	#read loop
        while not self._stopevent.isSet():
                try:
			tc=self.extractBLEval(self.cht.read())
			tmi=self.extractBLEval(self.chtmin.read())
			tma=self.extractBLEval(self.chtmax.read())
			bat=self.extractBLEval(self.chb.read())
			
			#gather battery percent
                	#val = binascii.b2a_hex(ww)
                	#val = binascii.unhexlify(val)
                	#val = struct.unpack('f', val)[0]
			#print "Batt=",float(val),"%"
			#self.batt = float(val)
			#return temperature
                        return tc,tmi,tma,bat

                except BTLEException as e:
                        print "BT READ - BTLEException : {0}".format(e)
                        if self.p != 0:
                                self.p.disconnect()

                except:
                        print 'BT READ - Other error! ',sys.exc_info()[0]

		#disconnect
                if self.p != 0:
	                self.p.disconnect()
                #wait 1 second before try again
                self._stopevent.wait(1)
		#reconnect
		self.connect()


    # compute mini and maxi values (Gene Cafe hack)
    # algoritm from evquink/RoastGenie (thank you!)
    def addValSMEM_old(self, val):
	currentT = time.time()

	#algorithm executed each 500ms minimum
	if ((currentT - self.previousT) > self.interval):
     		self.previousT = currentT
     		self.Tnow = val
     		self.TminLoopCount = self.TminLoopCount+1
     		self.TmaxLoopCount = self.TmaxLoopCount+1
     		self.T_dif_now = self.Tnow - self.Tlast
    		#print "tDifNow="+str(self.T_dif_now)
     		if (self.T_dif_now >= 0.0 and self.T_dif_last < 0.0 and self.TminLoopCount > 1):  # this is a local minimum
       			self.Tmin = self.Tlast                                                    # best estimate of environmental temp
       			self.TminLoopCount = 0                                                    # reset loop counter
			self.mData.setTempL(self.Tlast)
#			print "minimum detected:"+str(self.Tlast)
   
 		if (self.T_dif_now <= 0.0 and self.T_dif_last > 0.0 and self.TmaxLoopCount > 1):  # this is a local maximum
       			self.Tmax = self.Tlast                                                   # best estimate of bean mass temp
       			self.TmaxLoopCount = 0                                                   # reset loop counter
			self.mData.setTempH(self.Tlast)
#			print "maximum detected:"+str(self.Tlast)
      
     		self.Tlast = self.Tnow
     		self.T_dif_last = self.T_dif_now


    def run(self):
    	print "thread BT is readry!"
	retBTNOK = 1
	#try to connect to BT sensor
	self.connect()

	#do a 
	while not self._stopevent.isSet(): 
		#read BLE values
		tc,tmi,tma,bat = self.read()
		print (time.asctime( time.localtime(time.time()) ) + " Temp=" + str(tc) + " Tmin=" + str(tmi) + " Tmax=" + str(tma) + " Batt=" + str(bat))
		#upgrade data in shared memory 	
		self.mData.setAllData(tc,tmi,tma,bat)
		#wait a little
		self._stopevent.wait(1) 


    def stop(self): 
	print "stopping thread BT"
        self._stopevent.set( ) 
	if self.p != 0:
		self.p.disconnect()
