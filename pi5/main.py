#! /usr/bin/python
import os
import re
import cv2
import time
import pprint
import serial
import string
import pickle
import pynmea2
import imutils
import requests
import pyrebase
import face_recognition
from imutils import paths
from imutils.video import FPS
import speech_recognition as sr
from imutils.video import VideoStream
from gpiozero import Button, DistanceSensor, Buzzer

class Neutrack():                   
    def  __init__(self):
        #Setup pin for button, buzzer, and ultrasonic
        self.change_mode = Button(20)
        self.buzzer = Buzzer(23)
        self.ultrasonic = DistanceSensor(echo=17, trigger=4, threshold_distance=0.5)

        #Setup port for gps
        self.port = "/dev/ttyAMA0"
        self.ser=serial.Serial(self.port, baudrate=9600, timeout=0.5)

        #Setup firebase configuration
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
        self.api_key = "AIzaSyBgAmxCkLFhzG8xA2lo_4XYU2es8Y5NCXY"
        self.db = firebase.database()

        #Setup for face recognition
        self.setup_face()   

    def srf(self):
        while True:
            if self.ultrasonic.distance < 0.5:
                self.buzzer.on()
                print("in range")
            else:
                self.buzzer.off()
                print("out of range")    
        
    def location(self):
        pynmea2.NMEAStreamReader()
        newdata = self.ser.readline()
        
        if newdata[0:6] == b"$GPRMC":
            newmsg = pynmea2.parse(newdata.decode('utf-8'))
            # newmsg = pynmea2.parse(newdata.decode('latin-1'))
            lat=newmsg.latitude
            lng=newmsg.longitude
            gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
            print(gps)
            return lat, lng

    def select_mode(self):
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)         
            print("Please say something...")  
            os.system(f"espeak 'Select mode:'")       
            os.system(f"espeak '1. Get directions 2. Face recognition 3. Add New Face 4. Let me see the world'")   
            audio = r.listen(source)
                
            try:
                mode = r.recognize_google(audio)
                print("Mode : \n " + mode)
                if mode == "one":
                    self.get_path()
                elif mode == "two":
                    self.face_recog()
                elif mode == "three":
                    self.headshot()
                elif mode == "four":
                    self.srf()
                else:
                    os.system(f"espeak 'Sorry, I didn't catch that. Could you repeat, please?'")
                    self.select_mode()
            except Exception as e:
                os.system(f"espeak 'Sorry, I didn't catch that. Could you repeat, please?'")
                print("Error : " + str(e))
                self.select_mode()

    def get_destination(self):
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            
            print("Please enter your destination: ")
            os.system(f"espeak 'Please tell me your destination: '")           
            audio = r.listen(source)
            
            try:
                text = r.recognize_google(audio)
                print("You have said : \n " + text)
                return text     
            except Exception as e: 
                os.system(f"espeak 'Sorry, I didn't catch that. Could you repeat, please?'")
                print("Error : " + str(e))
                self.get_destination()

    def get_directions(self, start_location, end_location, api_key):
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
    
    def get_path(self):
        end_location = self.get_destination()

        while not self.button.is_pressed:
            try:
                lat, lng = self.location()
                start_location = f"{lat}, {lng}"
                directions = self.get_directions(start_location, end_location, self.api_key)
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
                self.db.update(data)
                print("Data sent")
                # os.system(f"espeak 'Data sent'")
                # pprint.pprint(data)
                # os.system(f"espeak 'Data: {data}'")
            except TypeError as e:
                print(f"An error occurred: {e}")
                os.system(f"espeak 'Sorry, i can't give you directions'")
                break
                
        self.select_mode()

    def setup_face(self):
        #Setup face recognition
        self.currentname = "unknown"
        encodingsP = "encodings.pickle"
        print("[INFO] loading encodings + face detector...")
        self.data = pickle.loads(open(encodingsP, "rb").read())
        self.vs = VideoStream(src=0,framerate=10).start()
        time.sleep(2.0)
        self.fps = FPS().start() 
            
    def shutdown_face(self):
        self.fps.stop()
        print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))

        cv2.destroyAllWindows()
        self.vs.stop()
         
    def face_recog(self):
        while not self.button.is_pressed:
            frame = self.vs.read()
            frame = imutils.resize(frame, width=500)
            boxes = face_recognition.face_locations(frame)
            encodings = face_recognition.face_encodings(frame, boxes)
            names = []

            for encoding in encodings:
                matches = face_recognition.compare_faces(self.data["encodings"],
                    encoding)
                name = "Stranger" #if face is not recognized, then print Unknown

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matchedIdxs:
                        name = self.data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    name = max(counts, key=counts.get)

                    if currentname != name:
                        currentname = name
                        print(f" This is {currentname}")
                        if currentname == "Veronica":
                            os.system(f"espeak 'This is Veronica Putri, GDE Android and Hackfestn 2024 Final Pitching Judge'")
                        elif currentname == "Riza":
                            os.system(f"espeak 'This is Riza Fahmi, GDE Web and Co-Founder of HacktivEight, also Hackfest 2024 Final Pitching Judge'")
                        elif currentname == "Dimas":
                            os.system(f"espeak 'This is Dimas Prasetyo, Senior Developer of Telkom Indonesia and Hackfest 2024 Final Pitching Judge'")
                        else:
                            os.system(f"espeak 'This is {currentname}'")

                names.append(name)

            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (0, 255, 255), 2)

            cv2.imshow("Facial Recognition is Running", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            self.fps.update()
        
        self.shutdown_face()
        self.select_mode()

    def train_face(self):
        print("[INFO] start processing faces...")
        imagePaths = list(paths.list_images("dataset"))

        knownEncodings = []
        knownNames = []

        for (i, imagePath) in enumerate(imagePaths):
            print("[INFO] processing image {}/{}".format(i + 1,
                len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]

            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            boxes = face_recognition.face_locations(rgb,
                model="hog")

            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)

        print("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open("encodings.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()

        os.system(f"espeak 'Training complete'")
        self.select_mode()

    def headshot(self):
        self.shutdown_face()
        name = 'Caroline'

        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("press space to take a photo", 500, 300)

        img_counter = 0

        print("setup complete")

        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("press space to take a photo", frame)

            k = cv2.waitKey(1)
            if k%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k%256 == 32:
                # SPACE pressed
                img_name = "dataset/"+ name +"/image_{}.jpg".format(img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1

        cam.release()

        cv2.destroyAllWindows()
        self.train_face()

if __name__ == '__main__':
    neutrack = Neutrack()
    neutrack.select_mode()