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
		self.aX = 0.0
		self.aY = 0.0
		self.aZ = 0.0
		self.motorP = 0
		self.heaterP = 0
		self.lok = threading.Lock()

	def setAllData(self, tc, tmi, tma, tba, az):
		#protect concurrent access with mutex
		self.lok.acquire()
		self.temp = tc
		self.tempL = tmi
		self.tempH = tma
		self.batt = tba
		self.aZ = az
		self.lok.release()

        def getAllData(self):
                #protect concurrent access with mutex
                self.lok.acquire()
                tc = self.temp 
                tmi = self.tempL 
                tma = self.tempH 
                tba = self.batt
                self.lok.release()
		return tc,tmi,tma,tba

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

	def setAccelX(self,ax):
                #protect concurrent access with mutex
                self.lok.acquire()
                self.aX = ax
                self.lok.release()

        def getAccelX(self):
                #protect concurrent access with mutex
                self.lok.acquire()
                xyz = self.aX
                self.lok.release()
                return xyz

	def setAccelY(self,ay):
                #protect concurrent access with mutex
                self.lok.acquire()
                self.aY = ay
                self.lok.release()

        def getAccelY(self):
                #protect concurrent access with mutex
                self.lok.acquire()
                xyz = self.aY
                self.lok.release()
                return xyz

	def setAccelZ(self,az):
                #protect concurrent access with mutex
                self.lok.acquire()
                self.aZ = az
                self.lok.release()

        def getAccelZ(self):
                #protect concurrent access with mutex
                self.lok.acquire()
                xyz = self.aZ
                self.lok.release()
                return xyz

        def setMotorP(self,mp):
                #protect concurrent access with mutex
                self.lok.acquire()
                self.motorP = mp
                self.lok.release()

        def getMotorP(self):
                #protect concurrent access with mutex
                self.lok.acquire()
                xyz = self.motorP
                self.lok.release()
                return xyz

        def setHeaterP(self,mp):
                #protect concurrent access with mutex
                self.lok.acquire()
                self.heaterP = mp
                self.lok.release()

        def getHeaterP(self):
                #protect concurrent access with mutex
                self.lok.acquire()
                xyz = self.heaterP
                self.lok.release()
                return xyz

	def setAccelYZ(self,ay,az):
                #protect concurrent access with mutex
                self.lok.acquire()
                self.aY = ay
                self.aZ = az
                self.lok.release()
