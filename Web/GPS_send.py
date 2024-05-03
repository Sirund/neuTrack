import pyrebase
import serial
import pynmea2

# firebaseConfig={
#   "apiKey": "AIzaSyArU2hVkqA7CCj00t26YzxSjyYx4TdmLs0",
#   "authDomain": "gps-tracker2-50503.firebaseapp.com",
#   "databaseURL": "https://gps-tracker2-50503-default-rtdb.firebaseio.com",
#   "projectId": "gps-tracker2-50503",
#   "storageBucket": "gps-tracker2-50503.appspot.com",
#   "messagingSenderId": "118394749599",
#   "appId": "1:118394749599:web:359b51af670a0d4e2ad8aa"
#     }

firebaseConfig = {
  "apiKey": "AIzaSyBGwuIcJfdcToqX3VqO84W5JPxXoNmHIJM",
  "authDomain": "gscmb-398aa.firebaseapp.com",
  "databaseURL": "https://gscmb-398aa-default-rtdb.firebaseio.com",
  "projectId": "gscmb-398aa",
  "storageBucket": "gscmb-398aa.appspot.com",
  "messagingSenderId": "200696319737",
  "appId": "1:200696319737:web:856b0ca6ffd400c5d39c28",
  "measurementId": "G-KQB9PNRBTH"
}

firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()

while True:
        port="/dev/ttyAMA0"
        ser=serial.Serial(port, baudrate=9600, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        newdata=ser.readline()
        n_data = newdata.decode('latin-1')
        if n_data[0:6] == '$GPRMC':
                newmsg=pynmea2.parse(n_data)
                lat=newmsg.latitude
                lng=newmsg.longitude
                gps = "Latitude=" + str(lat) + " and Longitude=" + str(lng)
                print(gps)
                data = {"LAT": lat, "LNG": lng}
                db.update(data)
                print("Data sent")
