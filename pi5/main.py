import os
import re
import cv2
import time
import pickle
import pprint
import serial
import engine
import imutils
import pynmea2
import pyttsx3
import pathlib
import pyrebase
import requests
import textwrap
import PIL.Image
import face_recognition
from imutils import paths
from imutils.video import FPS
import speech_recognition as sr
import google.generativeai as genai
from imutils.video import VideoStream
from gpiozero import Button, DistanceSensor, Buzzer

import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class Neutrack():                   
    def  __init__(self):
        #Setup pin for button, buzzer, and ultrasonic
        self.button = Button(21)
        self.buzzer = Buzzer(23)
        self.ultrasonic = DistanceSensor(echo=17, trigger=4, threshold_distance=0.5)

        #Setup port for gps
        self.ser = serial.Serial('/dev/ttyAMA0',
		                    baudrate=9600,
		                    parity=serial.PARITY_NONE,
		                    stopbits=serial.STOPBITS_ONE)

        #Setup for text to speech                    
        self.engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        self.engine.setProperty('voice', 'en-us')
        self.engine.setProperty('rate', 130)

		#Setup firebase
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

        firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = firebase.database()
        self.api_key = "AIzaSyBgAmxCkLFhzG8xA2lo_4XYU2es8Y5NCXY"

        #Setup gemini
        GOOGLE_API_KEY = "AIzaSyCBQ5PcFr7XnFz6HZDfDpS-RuFjxhp0WD8"
        genai.configure(api_key=GOOGLE_API_KEY)
        
        print("setup complete")

    def speak(self, text):
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def select_mode(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Select mode: ")
            self.speak("Select mode: ")

            print("1. Get directions")
            self.speak("Get directions")
            print("2. New face")
            self.speak("New face")
            print("3. Face recognition")
            self.speak("Face recognition")
            print("4. Let me see the world")
            self.speak("Let me see the world")
            print("5. Answer my question")
            self.speak("Answer my question")
            audio = r.listen(source)
            mode = r.recognize_google(audio)
            try:
                if mode == "Get directions":
                    self.get_path()
                elif mode == "New face":
                    self.new_face()
                elif mode == "Face recognition":
                    self.face_recog()
                elif mode == "Let me see the world":
                    self.vision()
                elif mode == "Answer my question":
                    self.gemini()
            except Exception as e:
                print("Error : " + str(e))

    def srf(self):
        while True:
            if self.ultrasonic.distance < 0.5:
                self.buzzer.on()
                print("in range")
            else:
                self.buzzer.off()
                print("out of range")     
 
    def get_directions(self, start_location, end_location):
        print("get direction")
        base_url = "https://maps.googleapis.com/maps/api/directions/json?"
        nav_request = "origin={}&destination={}&key={}".format(
            start_location.replace(" ", "+"),
            end_location.replace(" ", "+"),
            self.api_key
        )
        request = base_url + nav_request
        response = requests.get(request)
        directions = response.json()
        return directions
         
    def get_location(self):
        dataout = pynmea2.NMEAStreamReader()
        data = self.ser.readline()
        if data[0:6] == b"$GPRMC":
            try:
                msg = pynmea2.parse(data.decode('utf-8'))
                lat = msg.latitude
                lng = msg.longitude
                print(f"Latitude: {lat}, Longitude: {lng}")
                return lat, lng
            except pynmea2.ParseError as e:
                print(f"Parse error: {e}")
                self.speak("gps error")

    def get_destination(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Please enter your destination: ")
            self.speak("Please enter your destination: ")
            audio = r.listen(source)
            destination = r.recognize_google(audio)
            return destination
                
    def get_path(self):
        end_location = self.get_destination()
        while True:
            try:
                lat, lng = self.get_location()
                if (lat == 0.0) and (lng == 0.0):
                    print("gps lost signal")
                    self.speak("gps lost signal")
                    break
                start_location = f"{lat}, {lng}"
                print(start_location)
                directions = self.get_directions(start_location, end_location)
                route = directions['routes'][0]['legs'][0]
                print(f"Current location: {route['start_address']}")
                self.speak("Current location is {route['start_address']}")
                print(f"Destination: {route['end_address']}")
                self.speak("Destination is {route['end_address']}")
                print(f"Distance: {route['distance']['text']}")
                self.speak("Distance is {route['distance']['text']}")
                print(f"Duration: {route['duration']['text']}")
                self.speak("Duration is {route['duration']['text']}")
                print("Directions:")
                for step in route['steps']:
                    instructions = re.sub('<.*?>', '', step['html_instructions'])
                    print(instructions)
                    self.speak(instructions)
                    self.srf()
                    if self.button.is_pressed:
                        break
                data = {"LAT": lat, "LNG": lng, "Current Location": route['start_address']}
                self.db.update(data)
                print("Data sent")
                self.speak("Data sent")
            except TypeError as e:
                print(f"An error occurred: {e}")
                self.speak(f"error to get path")
                self.select_mode()
            
            if self.button.is_pressed:
                break
        
        self.select_mode()

    def get_name(self):
        r = sr.recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Please enter name: ")
            self.speak("Please enter name: ")
            audio = r.listen(source)
            name = r.recognize_google(audio)
            return name

    def new_face(self):
        name = self.get_name()
        
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("press button to take a photo", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("press button to take a photo", 500, 300)

        img_counter = 0

        folder_path = 'dataset/' + name

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print("Folder created successfully.")
        else:
            print("Folder already exists.")
        while img_counter != 10:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("press space to take a photo", frame)

            if self.button.is_pressed:
                # BUTTON pressed
                img_name = "dataset/"+ name +"/image_{}.jpg".format(img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1

        cam.release()
        cv2.destroyAllWindows()
        self.train_model()
        
    def train_model(self):
        print("[INFO] start processing faces...")
        imagePaths = list(paths.list_images("dataset"))

        knownEncodings = []
        knownNames = []

        for (i, imagePath) in enumerate(imagePaths):
                # extract the person name from the image path
                print("[INFO] processing image {}/{}".format(i + 1,
                        len(imagePaths)))
                name = imagePath.split(os.path.sep)[-2]
                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                boxes = face_recognition.face_locations(rgb, model="hog")

                encodings = face_recognition.face_encodings(rgb, boxes)

                for encoding in encodings:
                        knownEncodings.append(encoding)
                        knownNames.append(name)

        print("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open("encodings.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()
        print("Training is finished")
        
    def face_recog(self):
        currentname = "unknown"
        encodingsP = "encodings.pickle"

        print("[INFO] loading encodings + face detector...")
        data = pickle.loads(open(encodingsP, "rb").read())

        vs = VideoStream(src=0,framerate=10).start()
        time.sleep(2.0)

        fps = FPS().start()

        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
            boxes = face_recognition.face_locations(frame)
            encodings = face_recognition.face_encodings(frame, boxes)
            names = []

            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    
                    name = max(counts, key=counts.get)

                    if currentname != name:
                        currentname = name
                        print(f" This is {currentname}")
                        self.speak(f"This is {currentname}")
                
                print(f"this is {name}")

                names.append(name)

            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(frame, (left, top), (right, bottom),
                            (0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            .8, (0, 255, 255), 2)
                            
            cv2.imshow("Facial Recognition is Running", frame)
            if self.button.is_pressed:
                break

            fps.update()

        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        cv2.destroyAllWindows()
        vs.stop()
        self.select_mode()

    def get_question(self):
        r = sr.recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Please enter your question: ")
            self.speak("Please enter your question: ")
            audio = r.listen(source)
            question = r.recognize_google(audio)
            return question
        
    def gemini(self):
        question = self.get_question()
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(question)
        print(response)
        self.speak(response.text)
        self.select_mode()

    def vision(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            self.speak("Error: Could not open camera.")
            self.select_mode()
        
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('captured_image.jpg', frame)
            print("Image saved as 'captured_image.jpg'")

        cap.release()

        img = PIL.Image.open("captured_image.jpg")
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(img)
        print(response)
        self.speak(response.text)
        self.select_mode()


if __name__ == '__main__':
    neutrack = Neutrack()
    neutrack.select_mode()
    

