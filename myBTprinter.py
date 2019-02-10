# coding: utf-8
import bluetooth
import time
import genelogo
from datetime import datetime


#codes retour chariot
RC = chr(0x0A)  # retour a la ligne
FF = chr(0x0C)  # avance papier formfeed
#effets de texte
DH = chr(0x11)  # double hauteur (select/deselect)
DWS = chr(0x1E) # start double largeur
DWE = chr(0x1F) # end double largeur
INV = chr(0x12) # inverse video (select/deselect)

#
# Class to handle BTPrinter!
#
class Printer:
        def __init__(self):

		#largeur texte standard / double
		largTstd = 41
		largTdbl = 21

		#global socket
		self.sock = 0
		self.btext = ""


	#define is BT socket is connected
	def isConnected(self):
		try:
    			self.sock.getpeername()
    			return True
		except:
    			return False

	#BT connect to printer
	def myConnect(self):
		try:
			bd_addr = "00:11:67:E5:FE:87"
			self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
			self.sock.connect((bd_addr, 1)) #first port in bluetooth
			self.sock.set_l2cap_mtu(65535)
			self.sock.send("\x1bh1;") #fr config
		except Exception as e:
                	print "Connect Error: ",e

	#send data
	def mySend(self,data):
		#if not connected, reconnect!
		if(self.isConnected() == False):
			print "connecting..."
			self.myConnect()
		else:
			print "already connected, now send!"
		#try to send data
		try:
			print "sending ",len(data)," bytes"
			print self.sock.send(data), " bytes sent"
		except Exception as e:
			print "Send Error: ",e

	#print title in inverse big
	def printTitle(self,text):
		self.btext = self.btext + (INV+DH+DWS+text+DWE+DH+INV+RC)

	def printBig(self,text):
		self.btext = self.btext + (DH+text+DH+RC)

	def printLN(self,text):
		self.btext = self.btext + (text+RC)

	def printT(self,text):
		self.btext = self.btext + (text)

	def printFormfeed(self):
		self.mySend(self.btext + FF)
		self.btext = ""


	def printLogo(self):
		#get gene logo
		picstar = genelogo.pic
		picw = 23 #(140/6)
		pich = 71
		cmd = ""
		#send line by line
		for i in range(15):
			cmd = cmd + chr(0x1B)+"g"
			for i in range((i*picw),((i*picw)+picw)):
				cmd = cmd + chr(picstar[i] | 0x40)
			cmd = cmd + chr(0x29)
		self.mySend(cmd)		
		#time.sleep(0.1)

	def dispDlLogo(self):
		cmd = chr(0x1B)+"GP0,40;"
        	self.mySend(cmd)

	def dlLogo(self):
		#get gene logo
	        picstar = genelogo.picstar#picmaya8#picgene38#picstar28#picsimple8#picstar#pic8
		picw = 48#280#144#48#140 
		pich = 48#180#69#56#48#71
		cmd = chr(0x1B)+"GL2,0,"+str(picw)+","+str(pich)+";"
		print "DL logo len:", len(cmd)," lenPicstar", len(picstar)," cmd=",cmd
		self.mySend(cmd+''.join(map(chr,picstar[0:(picw/8)*pich])))
		print "DL finished! Now disp logo"
	#	dispDlLogo()

	def dispFullText(self,date,url,duree,tmax):
		#display logo
		dispDlLogo()
		time.sleep(1)
		#text
		printTitle("")
		printTitle("")
		printLN("Welcome to Matt Torrefactions!")
		printLN("")
		self.printTitle("Date: "+str(date))
		self.printBig("Origine: ______________________________")
       	 	self.printBig("Type:    lave   naturel   honey   blend")
        	self.printBig("Torre:   blond     1C       2C    dark")
		self.printLN("- - - - - - - - - - - - - - - - - - - - -")
		self.printLN(url)
		self.printLN("temps total:"+str(duree))
		self.printLN("tmax: "+str(tmax)+"C")
		self.printLN("ROR:")
		self.printLN("- - - - - - - - - - - - - - - - - - - - -")
		self.printBig("Poids initial:             g.")
		self.printBig("Poids final:               g.")
		self.printBig("Perte:                     %")
		self.printTitle("MAZZER              ")
		self.printBig("Crans:")
		self.printTitle("Evaluation          ")
		self.printBig("J+0:   1    2    3    4    5")
		self.printBig("J+ :   1    2    3    4    5")
		self.printBig("J+ :   1    2    3    4    5")
		self.printBig("J+ :   1    2    3    4    5")
		self.printLN("Commentaire libre:")
		self.printBig("")
		self.printBig("")
		self.printBig("")
		self.printBig("")
		self.printBig("")
		self.printTitle("THANK YOU, COME AGAIN")
		self.printFormfeed()
	

