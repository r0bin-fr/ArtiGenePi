import os
import glob
import time
import threading
import time
import sys
import readBT
import socket

#server values
HOST = ''        # Symbolic name meaning all available interfaces
PORT = 60016              # Arbitrary non-privileged port

class TaskServeur(threading.Thread): 

    def __init__(self, mData,sData): 
        threading.Thread.__init__(self) 
        self._stopevent = threading.Event( ) 
	self.mData = mData
	self.sData = sData
	self.s = 0
	self.conn = 0


    def run(self):
    	print "thread Server is readry!"

	# -------- Program Loop 1 -----------
	while not self._stopevent.isSet():
        	self.s = 0
        	print("TaskServer loop1 - start server")
        	#listen to socket
        	try:
                	self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                	self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                	self.s.bind((HOST, PORT))
                	self.s.listen(1)
                	break;
        	except socket.error as e:
                	print "TaskServer loop1 - Socket error : {0}".format(e)
                	if self.s != 0:
                	        self.s.close()
        	#wait 1 second before new attempt
		self._stopevent.wait(1) 

	# --------  Program Loop 2 -----------
	while not self._stopevent.isSet(): 
	        self.conn = 0
        	#print("TaskServer loop2 - now listening")

        	try:
                	self.conn, addr = self.s.accept()
                	print 'TaskServer loop2 - connected by', addr
                	#send temperature once and disconnect
                	#btemp = self.mData.getTempL()
                	#atemp = self.mData.getTempH()
                	btemp = self.mData.getAccelX()
                	atemp = self.mData.getAccelY()
			#atemp = self.sData.get_temp()
			heat = self.mData.getHeaterP()
                	self.conn.sendall(str(atemp)+","+str(btemp)+","+str(heat))

	        except socket.error as e:
        	        print "TaskServer loop2 - Socket error : {0}".format(e)
        	finally:
                	if self.conn != 0:
                        	#print "TaskServer loop2 - close socket"
                        	self.conn.close()

    def stop(self): 
	print "stopping thread Server"
        self._stopevent.set( ) 
	if self.conn != 0:
		self.conn.close()
	if self.s != 0:
                self.s.close()
