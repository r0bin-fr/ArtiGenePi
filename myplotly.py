#!/usr/bin/python
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls
import sys
import repr
from plotly.graph_objs import Scatter, Layout, Figure, Data, Stream, YAxis
from datetime import datetime
from dateutil.relativedelta import relativedelta
import myBTprinter



#
# Class to handle Plotly data for Artigene!
#
class MyPlotly:
	def __init__(self,doinit):
		#init vars
		self.lastZ = 0
		self.lastZ2 = 0
		self.myror = 0
		self.listT = [0]
		self.lastBT = 0	
		self.lastBTM = 0
		self.BTM = 0		
		self.deltaBT = 0
		self.deltaBTBak = 0
		self.weblink = ""
		self.btmax = 0
		#init timestamp
		self.ts = datetime.now()
		self.lastTime = 0
		#get my streams from config file
		self.pystream_ids = tls.get_credentials_file()['stream_ids']
		#print self.pystream_ids
		stream_token_tcurr = self.pystream_ids[0]
		stream_token_tmin = self.pystream_ids[1]
		stream_token_tmax = self.pystream_ids[2]
		stream_token_t2 = self.pystream_ids[3]
		stream_token_heater = self.pystream_ids[4]
		stream_token_ror = self.pystream_ids[5]
		stream_token_zaxis = self.pystream_ids[6]
		#torrefaction name
		self.torrename = "Torrefaction Artigene " +datetime.now().strftime("%d-%m-%Y %H:%M")
		#layout
		trace1 = go.Scatter(
    			x=[],
    			y=[],
    			name='BT (Tmin)',
    			stream=dict(
        			token=stream_token_tcurr,
        			maxpoints=10000
    			)
		)
		trace2 = go.Scatter(
                        x=[],
                        y=[],
                        name='BT moy',
                        stream=dict(
                                token=stream_token_tmin,
                                maxpoints=10000
                        )
                )
		trace3 = go.Scatter(
                        x=[],
                        y=[],
                        name='ET (Tmax)',
                        stream=dict(
                                token=stream_token_tmax,
                                maxpoints=10000
                        ),
                )
		trace4 = go.Scatter(
                        x=[],
                        y=[],
                        name='T ext',
                        stream=dict(
                                token=stream_token_t2,
                                maxpoints=10000
                        ),
                )
		trace5 = go.Bar(
		    	x=[],
		    	y=[],
		    	name='Heater',
	    		stream=dict(
        			token=stream_token_heater,
        			maxpoints=10000
    	    		),
    			yaxis='y2',
			opacity=0.4
		)
		trace6 = go.Scatter(
                        x=[],
                        y=[],
                        name='ROR',
                        stream=dict(
                                token=stream_token_ror,
                                maxpoints=10000
                        ),
			yaxis='y3'
                )
		trace7 = go.Scatter(
                        x=[],
                        y=[],
                        name='zaxis',
                        stream=dict(
                                token=stream_token_zaxis,
                                maxpoints=10000
                        ),
                        yaxis='y4'
                )

		layout = go.Layout(
			title=self.torrename,
    			yaxis=dict(
        			title='*C',
				domain=[0.3, 1]
    			),
    			yaxis2=dict(
        			title='heater level',
        			titlefont=dict(
            				color='rgb(148, 103, 189)'
        			),
        			tickfont=dict(
            				color='rgb(148, 103, 189)'
        			),
        			overlaying='y',
        			side='right'
    			),
			yaxis3=dict(
                                title='ROR',
				domain=[0, 0.3]
                        ),
			yaxis4=dict(
                                title='z-axis',
				overlaying='y3',
				side='right'
                        ),

		)

		#create figure object
		fig = Figure(data=[trace1, trace2, trace3, trace4, trace5, trace6,trace7], layout=layout)

		#opening streams
		try:
			if(doinit):
				print "Init Plotly figure and layout..."
				self.weblink = py.plot(fig, filename=self.torrename)
	        		print(self.weblink)
			print "Opening Plotly streams..."
        		self.stream_tcurr = py.Stream(stream_token_tcurr)
        		self.stream_tcurr.open()
        		self.stream_tmin = py.Stream(stream_token_tmin)
        		self.stream_tmin.open()
        		self.stream_tmax = py.Stream(stream_token_tmax)
        		self.stream_tmax.open()
        		self.stream_t2 = py.Stream(stream_token_t2)
        		self.stream_t2.open()
        		self.stream_heater = py.Stream(stream_token_heater)
        		self.stream_heater.open()
        		self.stream_ror = py.Stream(stream_token_ror)
        		self.stream_ror.open()
			self.stream_zaxis = py.Stream(stream_token_zaxis)
                        self.stream_zaxis.open()

			print "Plotly streams openned with success!"
		except Exception as e:
        		print "Plotly STREAMS unexpected error:", sys.exc_info()[0], " e=",e,"\n",repr(e)

		#printer object
		self.bprint = myBTprinter.Printer()

	#helper to update plotly streams with try catch 
	def updateStream(self,st,data):
		#heartbeat to keep stream openned if closed
		#try:
		#	st.heartbeat()
		#except:
		#	print ""		
		#send data through stream
		try:
			st.write(data)
		except Exception as e:
                	print "Plotly updateHELPER unexpected error:", sys.exc_info()[0], " e=",e,"\n",repr(e)

	#- met a jour le graphe
	def update(self,tcurr, tmin, tmax, t2, heater,zaxis):
		try:
			#time computation
			t_diff = relativedelta(datetime.now(),self.ts)

			#only update once per second
			if(self.lastTime != t_diff.seconds):
	                        pyi = ("%02d" % (t_diff.minutes)) + ":" + ("%02d" % (t_diff.seconds))
				#if(tcurr < 300) and (tcurr > 0):	
		                #        self.updateStream(self.stream_tcurr,{'x': pyi, 'y':  round(tcurr,1) })
				if(tmin < 300) and (tmin > 0):
					self.updateStream(self.stream_tcurr,{'x': pyi, 'y':  round(tmin,1) })
					if(tmin > self.btmax):
						self.btmax = tmin
				if(tmax < 300) and (tmax > 0):
                	        	self.updateStream(self.stream_tmax,{'x': pyi, 'y':  round(tmax,1) })
				if(t2 < 300) and (t2 > 0):
                	        	self.updateStream(self.stream_t2,{'x': pyi, 'y':  round(t2,1) })
                	        self.updateStream(self.stream_heater,{'x': pyi, 'y':  round(heater,1) })
				self.updateStream(self.stream_zaxis,{'x': pyi, 'y':  round(zaxis,1) })

				#update Bean Temp
                        	if (tmin < 300) and (tmin > 0):
                        		#check Zaxis pos: just after highest point was reached
                                	if (self.lastZ2 <= self.lastZ) and (zaxis < self.lastZ):
						#init data the first time
						if(self.lastBTM == 0):
							self.deltaBT = 0
							self.lastBTM = tmin
							self.BTM = tmin
							#print "init vars"
			             		else:
							val = ((tmin - self.lastBT) + self.deltaBTBak + self.deltaBTBak) 
							#print "val:",val
#                                        		self.deltaBT = ((tmin - self.lastBT) + self.deltaBTBak + self.deltaBTBak) / 3.0
							self.deltaBT = val / 3.0
                                        		self.BTM = self.lastBTM + self.deltaBT
						print "zaxis:",zaxis," self.lastZ:",self.lastZ," self.lastZ2:",self.lastZ2
						print "self.deltaBT:",self.deltaBT," self.lastBTM:",self.lastBTM," self.BTM:",self.BTM
						print "tmin:",tmin," self.lastBT:",self.lastBT," self.deltaBTBak:",self.deltaBTBak
                                        	#update stream
		                        	pyi = ("%02d" % (t_diff.minutes)) + ":" + ("%02d" % (t_diff.seconds))
                                        	self.updateStream(self.stream_tmin,{'x': pyi, 'y':  round(self.BTM,1) })                                     
                                        	#backup data
                                        	self.lastBT = tmin
                                        	self.deltaBTBak = self.deltaBT
                                        	self.lastBTM = self.BTM

				#ROR computation
				self.listT.append(self.BTM)
				
				#compute only with 30 seconds data
				if(len(self.listT) >= 30):
					self.myror = (self.BTM - self.listT.pop(0))
					#only update when BTM changes
					if(self.lastZ2 <= self.lastZ) and (zaxis < self.lastZ):
	                	        	self.updateStream(self.stream_ror,{'x': pyi, 'y':  round(self.myror,1) })
				else:
					self.updateStream(self.stream_ror,{'x': pyi, 'y': 0 })

				#backup data
				self.lastTime = t_diff.seconds
				self.lastZ2 = self.lastZ
				self.lastZ = zaxis

                except Exception as exep:
			print "err=",exep
                        print "Plotly UPDATE unexpected error:", sys.exc_info()[0]
	
	#print torre
	def printMyTorre(self):
		#time computation
                t_diff = relativedelta(datetime.now(),self.ts)
                pyi = ("%02d" % (t_diff.minutes)) + ":" + ("%02d" % (t_diff.seconds))
#                self.bprint.dispFullText(self.torrename,self.weblink,pyi,self.btmax)
                self.bprint.dispFullText(datetime.now().strftime("%d-%m-%Y %H:%M"),self.weblink,pyi,self.btmax)


	#- re-initie le timestamp (lorsque le roaster est connecte en BT)
	def initTimeStamp(self):
		self.ts = datetime.now()
		self.printMyTorre()

	#get weblink
	def getWeblink(self):
		return self.weblink

	#close plot data
	def closeStream(self):
		self.printMyTorre()
		try:	
                        self.stream_tcurr.close()
                        self.stream_tmin.close()
                        self.stream_tmax.close()
                        self.stream_t2.close()
                        self.stream_heater.close()
                        self.stream_ror.close()
                        self.stream_zaxis.close()
		except Exception as e:
                        print "err=" ,e,"\n",repr(e)
                        print "Plotly CLOSE unexpected error:", sys.exc_info()[0]

