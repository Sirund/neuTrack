#! /usr/bin/python
import os
import cv2
import time
import serial
import string
import pickle
import pynmea2
import imutils
import face_recognition
from imutils import paths

from imutils.video import FPS
from imutils.video import VideoStream
from gpiozero import Button, DistanceSensor, Buzzer

class Neutrack():
    def  __init__(self):
        #Setup pin for button, buzzer, and ultrasonic
        self.button = Button(20, hold_time=2)
        self.buzzer = Buzzer(23)
        self.ultrasonic = DistanceSensor(echo=17, trigger=4, threshold_distance=0.5)

        #Setup port for gps
        self.port = "/dev/ttyAMA0"
        self.ser=serial.Serial(self.port, baudrate=9600, timeout=0.5)

        #Setup face recognition
        self.currentname = "unknown"
        encodingsP = "encodings.pickle"
        print("[INFO] loading encodings + face detector...")
        self.data = pickle.loads(open(encodingsP, "rb").read())
        self.vs = VideoStream(src=0,framerate=10).start()
        time.sleep(2.0)
        self.fps = FPS().start()    

    def srf(self):
        while True:
            if self.ultrasonic.distance < 0.5:
                self.buzzer.on()
                print("in range")
            else:
                self.buzzer.off()
                print("out of range")    

    def location(self):
        while True:
            pynmea2.NMEAStreamReader()
            newdata = self.ser.readline()
            
            if newdata[0:6] == b"$GPRMC":
                newmsg = pynmea2.parse(newdata.decode('utf-8'))
                lat=newmsg.latitude
                lng=newmsg.longitude
                gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
                print(gps)
                return gps

    def resetup_face_recog(self):
        encodingsP = "encodings.pickle"
        print("[INFO] loading encodings + face detector...")
        self.data = pickle.loads(open(encodingsP, "rb").read())
        self.vs = VideoStream(src=0,framerate=10).start()
        time.sleep(2.0)
        self.fps = FPS().start()   
         
    def face_recog(self):
        while True:
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
        
        self.fps.stop()
        print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))

        cv2.destroyAllWindows()
        self.vs.stop()

    def 

if __name__ == '__main__':
    neutrack = Neutrack()
    neutrack.run()