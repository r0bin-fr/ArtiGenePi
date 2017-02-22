#!/usr/bin/env python

import time
import sys
import signal
import socket

#server values
HOST = 'localhost'        # Symbolic name meaning all available interfaces
PORT = 60016              # Arbitrary non-privileged port
conn = 0

# global values for data handling
done = False

#how to quit application nicely
def quitApplicationNicely():
	done = True
	time.sleep(0.1)
        sys.exit(0)

#signal handler
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
	quitApplicationNicely()

#intercept control c for nice quit
signal.signal(signal.SIGINT, signal_handler)


# -------- Main Program Loop -----------
#print("Client loop - connect to server")
#listen to socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
#print("Client loop - now connected!")

#listening loop
try:
	#receive data
	data = s.recv(1024)
	print str(data.decode('utf-8'))

except socket.error as e:
	print "Main loop - Socket error : {0}".format(e)		

s.close()

