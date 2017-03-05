import os
import glob
import time
import threading
import sys

 
class BTData:
	def __init__(self,temp=0):
		self.temp = temp
		self.tempL = temp
		self.tempH = temp
		self.batt = 0
		self.lok = threading.Lock()

	def setAllData(self, tc, tmi, tma, tba):
		#protect concurrent access with mutex
		self.lok.acquire()
		self.temp = tc
		self.tempL = tmi
		self.tempH = tma
		self.batt = tba
		self.lok.release()


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

