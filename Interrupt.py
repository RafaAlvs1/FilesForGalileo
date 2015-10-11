#!/usr/bin/env python
import sys
import serial
import time


galileo_path = "/media/mmcblk0p1/";
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

from pyGalileo import *


ser = serial.Serial('/dev/ttyGS0',115200)
pulsePin = A0


sampleCounter = 0
lastBeatTime = 0
firstBeat = True
secondBeat = False
Pulse = False

thresh = 2048
T = 2048
tT = 0
tTa = 0
P = 2048
tP = 0
A = 2048
tA = 0
tAa = 0
B = 0

IBI = 600


#def setup():


#def loop():


#def serialOutput(Signal):
	

# Decides How To OutPut BPM and IBI Data
def serialOutputWhenBeatHappens():
    # send heart rate with a 'B' prefix
    # send time between beats with a 'Q' prefix
    #sendDataToSerial(
    #  "DB" + String(BPM) + "Q" + String(IBI)
    #  + "P" + String(mP) + "T" + String(T) + "A" + String(A) + "s" + String(B)
    print 'manodu'
    ser.write(
    	'D' + str(IBI) + "." + str(P) + "." + str(A) + "." + str(T) + "." + str(B)
    	+ "." + str(BPM) )

def ISR():
	global sampleCounter, lastBeatTime, P, tP, T, tT, tTa, A, tA, tAa, B, tB, Pulse, IBI, thresh, secondBeat, firstBeat

	Signal = analogRead(pulsePin)               # read the Pulse Sensor
	#ser.write('S'+str(Signal)+'\r\n')
	#serialOutput(Signal)
	sampleCounter += 2                          # keep track of the time in mS with this variable
	N = sampleCounter - lastBeatTime;           # monitor the time since the last beat to avoid noise


	# find the points of interest of the pulse wave
	if Signal < thresh & N > (IBI/5)*3:       	# avoid dichrotic noise by waiting 3/5 of last IBI
		if (Signal < T & Signal > 0):           # T is the trough
			T = Signal                         	# keep track of lowest point in pulse wave
			tT = N

	if Signal > thresh & Signal > P:          	# thresh condition helps avoid noise
		P = Signal                             	# P is the peak
		tP = N
	
	if Signal < thresh & N <= (IBI/5)*2:       	# .. 
		if Signal < A & Signal > 0:             # .. 
			A = Signal                         	# .. 
			tA = N


	if N > tAa & N < tTa:
		if Signal > B:          				# ..
			B = Signal                          # ..
			tB = N								# ..

	#  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
	# signal surges up in value every time there is a pulse
	if N > 250:                                   # avoid high frequency noise
		#print N, (IBI/5)*3, Pulse, Signal, thresh
		if  (Signal > thresh) & (Pulse == False) & (N > (IBI/5)*3) :
			Pulse = True                                # set the Pulse flag when we think there is a pulse
			IBI = sampleCounter - lastBeatTime          # measure time between beats in mS
			lastBeatTime = sampleCounter                # keep track of time for next pulse

			if(secondBeat):                        		# if this is the second beat, if secondBeat == TRUE
				secondBeat = False                  	# clear secondBeat flag
				#for(int i=0; i<=9; i++):             	# seed the running total to get a realisitic BPM at startup
				#	rate[i] = IBI                      

			if(firstBeat):                         		# if it's the first time we found a beat, if firstBeat == TRUE
				firstBeat = False                   	# clear firstBeat flag
				secondBeat = True                   	# set the second beat flag
				return                              	# IBI value is unreliable so discard it


	#		# keep a running total of the last 10 IBI values
	#		word runningTotal = 0 						# clear the runningTotal variable    

	#		for(int i=0; i<=8; i++):                	# shift data in the rate array
	#			rate[i] = rate[i+1]                  	# and drop the oldest IBI value 
	#			runningTotal += rate[i]              	# add up the 9 oldest IBI values

	#		rate[9] = IBI	                          	# add the latest IBI to the rate array
	#		runningTotal += rate[9]	                	# add the latest IBI to runningTotal
	#		runningTotal /= 115200                     	# average the last 10 IBI values 
	#		BPM = 60000/runningTotal	               	# how many beats can fit into a minute? that's BPM!
	#		QS = True 	                             	# set Quantified Self flag
	#		# QS FLAG IS NOT CLEARED INSIDE THIS ISR


	print Signal, thresh, Pulse

	if Signal < thresh & Pulse == True:   			# when the values are going down, the beat is over
		Pulse = False                         			# reset the Pulse flag so we can do it again
		amp = P - T                           			# get amplitude of the pulse wave
		thresh = amp/2 + T                    			# set thresh at 50% of the amplitude
		#mP=P
		serialOutputWhenBeatHappens()   				# A Beat Happened, Output that to serial.
		P = thresh                            			# reset these for next time
		T = thresh
		A = thresh
		B = 0
		tAa = tA
		tTa = tT

	if (N > 2500):                           			# if 2.5 seconds go by without a beat
		thresh = 2048                          			# set thresh default
		P = 2048                               			# set P default
		T = 2048                               			# set T default
		A = 2048
		B = 0
		tAa = 0
		tTa = 0
		lastBeatTime = sampleCounter          			# bring the lastBeatTime up to date        
		firstBeat = True                      			# set these to avoid noise
		secondBeat = False                    			# when we get the heartbeat back

#When the file is run from the command line, this fucntion will execute.
#This function just calls setup once, then calls loop over and over. 
if __name__ == "__main__":

	#setup();
    while(1):
    	#loop()
        ISR()
        time.sleep (2.0 / 1000.0)