import os
import re
import cv2
import time
import pickle
import pprint
import serial
import imutils
import pynmea2
import pyrebase
import requests
import face_recognition
from imutils import paths
from imutils.video import FPS
from imutils.video import VideoStream
from gpiozero import Button, DistanceSensor, Buzzer

import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class Neutrack():                   
    def  __init__(self):
        #Setup pin for button, buzzer, and ultrasonic
        #self.button = Button(20)
        #self.buzzer = Buzzer(23)
        #self.ultrasonic = DistanceSensor(echo=17, trigger=4, threshold_distance=0.5)

        #Setup port for gps
        self.ser = serial.Serial('/dev/ttyAMA0',
		                    baudrate=9600,
		                    parity=serial.PARITY_NONE,
		                    stopbits=serial.STOPBITS_ONE)
		                    
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
        
        print("setup complete")
 
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
                
    def get_path(self):
        end_location = input("Please enter your destination: ")
        while True:
            try:
                lat, lng = self.get_location()
                start_location = f"{lat}, {lng}"
                print(start_location)
                directions = self.get_directions(start_location, end_location)
                route = directions['routes'][0]['legs'][0]
                print(f"Current location: {route['start_address']}")
                #os.system(f"espeak 'Current location is {route['start_address']}'")
                print(f"Destination: {route['end_address']}")
                #os.system(f"espeak 'Destination is {route['end_address']}'")
                print(f"Distance: {route['distance']['text']}")
                #os.system(f"espeak 'Distance is {route['distance']['text']}'")
                print(f"Duration: {route['duration']['text']}")
                #os.system(f"espeak 'Duration is {route['duration']['text']}'")
                print("Directions:")
                for step in route['steps']:
                    instructions = re.sub('<.*?>', '', step['html_instructions'])
                    print(instructions)
                    #os.system(f"espeak '{instructions}'")
                data = {"LAT": lat, "LNG": lng, "Current Location": route['start_address']}
                self.db.update(data)
                print("Data sent")
                #os.system(f"espeak 'Data sent'")
                pprint.pprint(data)
                #os.system(f"espeak 'Data: {data}'")
            except TypeError as e:
                print(f"An error occurred: {e}")
                #os.system(f"espeak 'An error occurred: {e}'")
                
    def new_face(self):
        name = input("Your name: ")
        
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("press space to take a photo", 500, 300)

        img_counter = 0

        while img_counter != 10:
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
                        print(currentname)

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

            fps.update()

        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        cv2.destroyAllWindows()
        vs.stop()
                
if __name__ == '__main__':
    neutrack = Neutrack()
    neutrack.face_recog()
    

