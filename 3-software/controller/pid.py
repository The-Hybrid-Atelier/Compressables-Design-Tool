#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Programmable Air Squeeze Interaction Detector
# Two threads control this detector.

# The classifier thread used a CURRENT_WINDOW of data to determine
# squeeze state. 

# The window-cleaner thread interfaces with the HAWS server to gather
# data from the Programmable Air pressure sensor and keeps the WINDOW_SIZE
# most recent packets stored in the CURRENT_WINDOW variable. 

# Classifier is called opportunistically i.e. when compute resources are available.
# TODO: This should be dialed to fit the interaction period. 

# Derived from: https://gist.github.com/ruedesign/5218221

from haws import *
from log import *
import threading
from scipy import stats
from simple_pid import PID
from IPython.display import display, clear_output

# Gesture Tracking Globals
SCALE = 4
Kp = 3 * SCALE
Ki = 0.1 * SCALE
Kd = 0.05 * SCALE

CURRENT_WINDOW = np.array([])
CURRENT_TIMES = np.array([])
STEP_SIZE = 0.250 #
PACKETS_RECEIVED = 0
WINDOW_SIZE = 0.330 # seconds
PACKET_SIZE = 8 # Number of sampled points in a single message
LAST_PRESSURE_READING = 0
DELAY = 0.05 # Artificial delay to prevent throttling threads
process_start = time.time()

# HAWS Metadata
DEVICE_NAME= "programmable-air"
uri = "ws://162.243.120.86:3001"
# uri = "ws://192.168.1.4:3001"
jws = JSONWebSocketClient("pid-controller", uri)
jws.connect()
pumpoff = {"api":{"command":"ALL_PUMP_OFF","params":{}}}
jws.send(pumpoff)
jws.send({"api":{"command":"PUMP_ON","params":{"pumpNumber":2, "PWM": 0}}})




# This thread starts JWS and pressure readings. It keeps the most recent current packets
# in CURRENT_WINDOW which is of size WINDOW_SIZE (seconds)

pressure_ON = {"api":{"command":"PRESSURE_ON","params":{}}}
pressure_OFF = {"api":{"command":"PRESSURE_OFF","params":{}}}

class thread_window_cleaner(threading.Thread):
	def __init__(self, thread):
		threading.Thread.__init__(self)
		self.name = "window_cleaner"
		self.kill_received = False
		self.pid_thread = thread

	def run(self):
		print("Connecting to HAWS at %s", uri)
		jws.connect()
		print("Turning on pressure readings...")
		jws.send(pressure_ON)
		jws.on(DEVICE_NAME, "read-pressure", self.recognition_routine_handler)
		jws.on("interaction-app", "pid", self.pid_thread.pid_message_handler)
		print("Listening...")
		while not self.kill_received:
			# print(self.name, "is active")
			jws.listen()
			# time.sleep(DELAY)
		jws.send(pressure_OFF)  
		pumpoff = {"api":{"command":"ALL_PUMP_OFF","params":{}}}
		jws.send(pumpoff)
		# jws.close()

	def recognition_routine_handler(self, jws, message):
		global CURRENT_WINDOW
		global CURRENT_TIMES
		global PACKETS_RECEIVED
		global LAST_PRESSURE_READING
		now = time.time()
		window_start = now - WINDOW_SIZE
		# REMOVE ANY OLD VALUES
		if len(CURRENT_TIMES) > 0 and len(CURRENT_WINDOW) > 0:
			np.argmax(CURRENT_TIMES > window_start)
			a = np.argmax(CURRENT_TIMES > window_start)
			CURRENT_TIMES = CURRENT_TIMES[a:]
			CURRENT_WINDOW = CURRENT_WINDOW[a*PACKET_SIZE:]
		# APPEND NEW VALUES
		CURRENT_TIMES = np.append(CURRENT_TIMES, now)
		CURRENT_WINDOW = np.append(CURRENT_WINDOW, message["data"])
		PACKETS_RECEIVED = PACKETS_RECEIVED + 1
		LAST_PRESSURE_READING = np.mean(message["data"])

		
class thread_classifer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
		self.name = "classifier"
		self.kill_received = False
		self.step_size = 0.1
		self.last_error = 0
		self.log = Log("Threaded PID", self.step_size)
		self.pid = PID(Kp, Ki, Kd, setpoint=132)
		self.pid.output_limits = (20, 100) 
		self.state = None
		self.last_act = 0
		self.pwm = 0
		self.stopped = False
		self.pid_stopped = False

	def pid_message_handler(self, jws, message):
		# print("IA: %s %s %s", (message, message["action"], message["value"]))
		if message["action"] == "set_setpoint":
			print("Changing setpoint to", message["value"])
			self.pid.setpoint = message["value"]
			self.pwm = message["value"]
		if message["action"] == "tunings":
			self.pid.tunings = tuple(message["value"])
			print("Changing tunings to", message["value"])
		if message["action"] == "emergency_stop":
			self.emergency_stop()
		if message["action"] == "restart":
			self.restart()
		if message["action"] == "pid_stop":
			print("PID STOPPED")
			self.pid_stopped = True
			pid = {"event": "pid-read", "data": [self.last_act]}
			jws.send(pid)
		if message["action"] == "pid_start":
			print("PID STARTED")
			self.pid_stopped = False

	def restart(self):
		self.stopped = False

	def emergency_stop(self):
		self.act(0)
		pumpoff = {"api":{"command":"ALL_PUMP_OFF","params":{}}}
		jws.send(pumpoff)
		self.state = "vent"
		vent = {"api":{"command":"VENT","params":{}}}
		jws.send(vent)
		self.stopped = True

	def act(self, pwm):
		if self.stopped:
			print('EMERGENCY STOP')
			return

		# pwm += 30
		if pwm > 100: 
			pwm = 100
		elif pwm < -100:
			pwm = -100

		if pwm > 0: # Blow	
			print("BLOW")
			if self.state != "blow":
				blow = {"api":{"command":"BLOW","params":{}}}
				jws.send(blow)
				self.state = "blow"
				jws.send({"api":{"command":"PUMP_ON","params":{"pumpNumber":1, "PWM": 0}}})
			

			# To prevent throttling:
			# if np.abs(self.last_act - pwm) > 1:
			jws.send({"api":{"command":"PUMP_ON","params":{"pumpNumber":2, "PWM": pwm}}})
			self.last_act = pwm

			return pwm
		else: 
			print("SUCK")
			if self.state != "suck":
				suck = {"api":{"command":"SUCK","params":{}}}
				jws.send(suck)
				self.state = "suck"
				jws.send({"api":{"command":"PUMP_ON","params":{"pumpNumber":2, "PWM": 0}}})
			

			# To prevent throttling:
			# if np.abs(self.last_act - pwm) > 1:
			jws.send({"api":{"command":"PUMP_ON","params":{"pumpNumber":1, "PWM": abs(pwm)}}})
			self.last_act = pwm
		
			return abs(pwm)

	def run(self):
		while not self.kill_received:
			# print(self.name, "is active")
			# time.sleep(DELAY)
			count = 0
			if(len(CURRENT_WINDOW) == 0):
				count = count + 1
				print("No sensor values detected... %i"%(count))
			else:
				# PID
				# if True and not (self.stopped or self.pid_stopped):
				# 	# process_value = np.mean(CURRENT_WINDOW)
				# 	process_value = LAST_PRESSURE_READING
				# 	error = self.pid.setpoint - process_value
				# 	clear_output(wait=True)

				# 	pwm = self.pid(process_value)
				# 	# print(process_value, pwm)
				# 	pwm = self.act(pwm)
				# 	# print(self.pid.tunings)

				# 	time.sleep(self.step_size)
				# 	process_value = LAST_PRESSURE_READING
				# 	display("PID(%i) %2.2f: %2.2f %2.2f --> %2.2f PWM" % (PACKETS_RECEIVED, self.pid.setpoint, process_value, error, pwm))
				# 	self.log.add(time.time(), self.pid.setpoint, process_value, pwm)	
				# else:
				# 	self.classify()
				# PWM
				if True and not (self.stopped or self.pid_stopped):
					# process_value = np.mean(CURRENT_WINDOW)
					# process_value = LAST_PRESSURE_READING
					# error = self.pid.setpoint - process_value
					clear_output(wait=True)
					# pwm = self.pid(process_value)
					# print(process_value, pwm)
					pwm = self.act(self.pwm)
					# print(self.pid.tunings)
					time.sleep(self.step_size)
					process_value = LAST_PRESSURE_READING
					display("PWM(%i) %2.2f --> %2.2f PWM --> %2.2f PWM" % (PACKETS_RECEIVED, process_value, self.pwm, pwm))
					# self.log.add(time.time(), self.pid.setpoint, process_value, pwm)	
				else:
					self.classify()


		# self.log.plot()
			# self.classify()

	def classify(self):
		global CURRENT_TIMES
		global WINDOW_SIZE
		# print("Classify")
		if len(CURRENT_TIMES) == 0:
			return
		if (time.time() - np.min(CURRENT_TIMES)) > WINDOW_SIZE:
			self.recognize()

	def recognize(self):
		global CURRENT_WINDOW
		pass
		# print("recognize", len(CURRENT_WINDOW), np.mean(CURRENT_WINDOW))
		# print(stats.describe(CURRENT_WINDOW))

# RUN THIS CELL TO ACTIVATE PID 
def has_live_threads(threads):
	return True in [t.isAlive() for t in threads]

# DO NOT TOUCH MAIN
def main():  
	threads = []
	tc = thread_classifer()

	for thread in (thread_window_cleaner(tc), tc):
		thread.start()
		threads.append(thread)

	while has_live_threads(threads):
		try:
			# synchronization timeout of threads kill
			[t.join(1) for t in threads
			 if t is not None and t.isAlive()]
		except KeyboardInterrupt:
			# Ctrl-C handling and send kill to threads
			print("Sending kill to threads...")

			for t in threads:
				t.kill_received = True
	jws.connect()
	jws.send(pressure_OFF)  
	pumpoff = {"api":{"command":"ALL_PUMP_OFF","params":{}}}
	jws.send(pumpoff)
	jws.close()
	print("Exited")
	
if __name__ == '__main__':
	print('Starting controller...')
	main()