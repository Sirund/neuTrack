import pyrebase
import serial
import pynmea2
import requests
import pprint
import os
import re
import speech_recognition as sr

def get_text_input():
    return input("Please enter your destination: ")

def get_audio_input():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        
        print("Please enter your destination: ")
        
        audio = r.listen(source)
        
        
        try:
            text = r.recognize_google(audio)
            print("You have said : \n " + text)
            return text
            
        
        except Exception as e:
            
            print("Error : " + str(e))

end_location = get_audio_input()

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

api_key = "AIzaSyBgAmxCkLFhzG8xA2lo_4XYU2es8Y5NCXY"

def get_directions(start_location, end_location, api_key):
    base_url = "https://maps.googleapis.com/maps/api/directions/json?"
    nav_request = "origin={}&destination={}&key={}".format(
        start_location.replace(" ", "+"),
        end_location.replace(" ", "+"),
        api_key
    )
    request = base_url + nav_request
    response = requests.get(request)
    directions = response.json()
    return directions

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

while True:
    try:
        port = "/dev/ttyAMA0"
        ser = serial.Serial(port, baudrate=9600, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        newdata = ser.readline()
        n_data = newdata.decode('latin-1')
        if n_data[0:6] == '$GPRMC':
            newmsg = pynmea2.parse(n_data)
            lat = newmsg.latitude
            lng = newmsg.longitude
            start_location = f"{lat}, {lng}"
            directions = get_directions(start_location, end_location, api_key)
            route = directions['routes'][0]['legs'][0]
            print(f"Current location: {route['start_address']}")
            os.system(f"espeak 'Current location is {route['start_address']}'")
            print(f"Destination: {route['end_address']}")
            os.system(f"espeak 'Destination is {route['end_address']}'")
            print(f"Distance: {route['distance']['text']}")
            os.system(f"espeak 'Distance is {route['distance']['text']}'")
            print(f"Duration: {route['duration']['text']}")
            os.system(f"espeak 'Duration is {route['duration']['text']}'")
            print("Directions:")
            for step in route['steps']:
                instructions = re.sub('<.*?>', '', step['html_instructions'])
                print(instructions)
                os.system(f"espeak '{instructions}'")
            data = {"LAT": lat, "LNG": lng, "Current Location": route['start_address']}
            db.update(data)
            print("Data sent")
            os.system(f"espeak 'Data sent'")
            pprint.pprint(data)
            os.system(f"espeak 'Data: {data}'")
    except TypeError as e:
        print(f"An error occurred: {e}")
        os.system(f"espeak 'An error occurred: {e}'")
