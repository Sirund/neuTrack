import pyrebase
import serial
import pynmea2

firebaseConfig = {
  "apiKey": "AIzaSyD-JfCXSHovjysfeiw42SWpQl8DoVN4704",
  "authDomain": "gps3-4ae0d.firebaseapp.com",
  "databaseURL": "https://gps3-4ae0d-default-rtdb.firebaseio.com",
  "projectId": "gps3-4ae0d",
  "storageBucket": "gps3-4ae0d.appspot.com",
  "messagingSenderId": "735625049442",
  "appId": "1:735625049442:web:afd757568a6d24ce03a83b",
  "measurementId": "G-HCF3MLT471"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

ser = serial.Serial('/dev/ttyAMA0',
		    baudrate=115200,
		    parity=serial.PARITY_NONE,
		    stopbits=serial.STOPBITS_ONE)

while True:
	dataout = pynmea2.NMEAStreamReader()
	data = ser.readline()
	text = data.decode('latin-1').strip()
	if text.startswith('$GNGLL'):
		try:
			msg=pynmea2.parse(text)
			lat=msg.latitude
			lng=msg.longitude
			print(f"Latitude: {lat}, Longitude: {lng}")
			data = {"LAT": lat, "LNG": lng}
			db.update(data)
			print("Data sent")
		except pynmea2.ParseError as e:
			print(f"Parse error: {e}")

