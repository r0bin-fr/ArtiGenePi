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


#
# Class to handle Plotly data for Artigene!
#
class MyPlotly:
	def __init__(self,doinit):
		#init timestamp
		self.ts = datetime.now()
		#get my streams from config file
		self.pystream_ids = tls.get_credentials_file()['stream_ids']
		#print self.pystream_ids
		stream_token_tcurr = self.pystream_ids[0]
		stream_token_tmin = self.pystream_ids[1]
		stream_token_tmax = self.pystream_ids[2]
		stream_token_t2 = self.pystream_ids[3]
		stream_token_heater = self.pystream_ids[4]
		#layout
		trace1 = go.Scatter(
    			x=[],
    			y=[],
    			name='T curr',
    			stream=dict(
        			token=stream_token_tcurr,
        			maxpoints=10000
    			)
		)
		trace2 = go.Scatter(
                        x=[],
                        y=[],
                        name='BT (T min)',
                        stream=dict(
                                token=stream_token_tmin,
                                maxpoints=10000
                        )
                )
		trace3 = go.Scatter(
                        x=[],
                        y=[],
                        name='ET (T max)',
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
		trace5 = go.Scatter(
		    	x=[],
		    	y=[],
		    	name='Heater',
	    		stream=dict(
        			token=stream_token_heater,
        			maxpoints=10000
    	    		),
    			yaxis='y2'
		)

		layout = go.Layout(
			title='My coffee roasts',
    			yaxis=dict(
        			title='*C',
				domain=[0.55, 1]
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
        			side='right',
    			)
		)

		#create figure object
		fig = Figure(data=[trace1, trace2, trace3, trace4, trace5], layout=layout)

		#opening streams
		try:
			if(doinit):
				print "Init Plotly figure and layout..."
	        		print(py.plot(fig, filename='Mes torres plotly'))
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

			print "Plotly streams openned with success!"
		except Exception as e:
        		print "Plotly STREAMS unexpected error:", sys.exc_info()[0], " e=",repr(e)

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
                	print "Plotly updateHELPER unexpected error:", sys.exc_info()[0], " e=",repr(e)

	#- met a jour le graphe (simple, hors extraction)
	def update(self,tcurr, tmin, tmax, t2, heater):
		try:
			t_diff = relativedelta(datetime.now(),self.ts)
                        pyi = ("%02d" % (t_diff.minutes)) + ":" + ("%02d" % (t_diff.seconds))
                        self.updateStream(self.stream_tcurr,{'x': pyi, 'y':  round(tcurr,1) })
                        self.updateStream(self.stream_tmin,{'x': pyi, 'y':  round(tmin,1) })
                        self.updateStream(self.stream_tmax,{'x': pyi, 'y':  round(tmax,1) })
                        self.updateStream(self.stream_t2,{'x': pyi, 'y':  round(t2,1) })
                        self.updateStream(self.stream_heater,{'x': pyi, 'y':  round(heater,1) })
                except Exception as e:
			print "err=" ,repr(e)
                        print "Plotly UPDATE unexpected error:", sys.exc_info()[0]

	#- re-initie le timestamp (lorsque le roaster est connecte en BT)
	def initTimeStamp(self):
		self.ts = datetime.now()
