import serial
import time
import string
import pynmea2

port="/dev/ttyAMA0"
ser=serial.Serial(port, baudrate=9600, timeout=0.5)

while True:
    dataout = pynmea2.NMEAStreamReader()
    newdata=ser.readline()
    
    if newdata[0:6] == b"$GPRMC":
        newmsg = pynmea2.parse(newdata.decode('utf-8'))
        lat=newmsg.latitude
        lng=newmsg.longitude
        gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
        print(gps)
