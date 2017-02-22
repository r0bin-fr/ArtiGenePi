import readBT
import multithreadBT
import time
import sys
import signal
import socket

#server values
HOST = ''        # Symbolic name meaning all available interfaces
PORT = 60016              # Arbitrary non-privileged port
conn = 0

# global values for data handling
maximT = readBT.BTData(0)
taskT = multithreadBT.TaskPrintTemp(maximT)
done = False

#how to quit application nicely
def quitApplicationNicely():
	done = True
	taskT.stop()
	time.sleep(0.1)
        sys.exit(0)

#signal handler
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
	quitApplicationNicely()

#intercept control c for nice quit
signal.signal(signal.SIGINT, signal_handler)


#start BT task
taskT.start()

# -------- Main Program Loop 1 -----------
while not done:
	s = 0
	print("Main loop1 - start server")
	#listen to socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
		s.listen(1)
		break;		
	except socket.error as e:
		print "Main loop1 - Socket error : {0}".format(e)		
		if s != 0:
			s.close()
	#wait 1 second before new attempt
	time.sleep(1)

# -------- Main Program Loop 2 -----------
while not done:	
	conn = 0
	print("Main loop2 - now listening")

	try:
		conn, addr = s.accept()
		print 'Main loop2 - connected by', addr

		#send temperature once and disconnect
		btemp = maximT.getTempL()  
		atemp = maximT.getTempH()  
		conn.sendall(str(atemp)+","+str(btemp))

	except socket.error as e:
		print "Main loop2 - Socket error : {0}".format(e)		
	finally:
		if conn != 0:
			print "Main loop2 - close socket"
			conn.close()


