import os
import glob
import time
import threading
import sys

 
class BTData:
	def __init__(self,temp=0):
		self.tempL = temp
		self.tempH = temp
		self.lok = threading.Lock()

	def setTempL(self,temp):
		#protect concurrent access with mutex
		self.lok.acquire()
		self.tempL = temp
		self.lok.release()

	def setTempH(self,temp):
		#protect concurrent access with mutex
		self.lok.acquire()
		self.tempH = temp
		self.lok.release()

	def getTempH(self):
		#protect concurrent access with mutex
		self.lok.acquire()
		xyz = self.tempH
		self.lok.release()
		return xyz

	def getTempL(self):
		#protect concurrent access with mutex
		self.lok.acquire()
		xyz = self.tempL
		self.lok.release()
		return xyz

