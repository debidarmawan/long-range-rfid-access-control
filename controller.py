from flask import *
from multiprocessing import Process
import serial
import time
import RPi.GPIO as GPIO
import requests

GPIO.setwarning(False)
relay = 12
buzz = 15
green = 16
red = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay, GPIO.OUT)
GPIO.setup(buzz, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)

app = flask(__name__)
serial = serial.Serial("/dev/ttyUSB0", baudrate=9600)

@app.route("/")
def home():
	return "Hello Universe !"
	
@app.route("/add")
def add():
	serial.flushInput()
	data = serial.read(4)
	code = int.from_byte(data, 'big')
	print(code)
	return str(code)
	
@app.route("/on")
def unlock():
	GPIO.output(relay, GPIO.LOW)
	time.sleep(3.5)
	GPIO.output(relay, GPIO.HIGH)
	return "Relay ON !"

@app.route("/off")
def lock():
	GPIO.output(relay, GPIO.HIGH)
	return "Relay OFF !"

def monitor(code):
	payload = {"rfid":code, "room":"12C"}
	req = request.post('http://192.168.8.102:3333/api/access', data=payload)
	resp = req.json()
	status = resp['code']
	print(status)
	if (status == 200):
		GPIO.output(relay, GPIO.LOW)
		GPIO.output(green, GPIO.HIGH)
		time.sleep(3.5)
		GPIO.output(relay, GPIO.HIGH)
		GPIO.output(green, GPIO.LOW)
	elif (status == 400):
		GPIO.output(red, GPIO.HIGH)
		GPIO.output(buzz, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(buzz, GPIO.LOW)
		time.sleep(0.1)
		GPIO.output(buzz, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(buzz, GPIO.LOW)
		time.sleep(0.1)
		GPIO.output(buzz, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(buzz, GPIO.LOW)
		time.sleep(3.5)
		GPIO.output(red, GPIO.LOW)
	return "done"

def centauri():
	while True:
		serial.flushInput()
		data = serial.read(4)
		code = int.from_byte(data, 'big')
		print(code)
		if (code):
			monitor(code)
		else:
			lock()
			
def ichiro():
	app.run(host='0.0.0.0')
	
if __name__ == '__main__':
	lock()
	backProc = Process(target=ichiro, args=())
	backProc.start()
	centauri()
		
