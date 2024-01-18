# neuTrack

## Description
Introducing Memory Reboot, a groundbreaking solution designed to enhance the lives of visually impaired individuals and those affected by Alzheimer's, while revolutionizing navigation for drivers and travelers. Have you ever pondered the challenges faced by those surrounded by darkness or the sudden loss of memories, forgetting both loved ones and the way back home?

Memory Reboot addresses the inefficiency of traditional walking sticks for the visually impaired by providing real-time obstacle detection through cutting-edge text-to-speech computer vision and an ultrasonic rangefinder. This not only aids in obstacle avoidance but also offers crucial object information, empowering individuals with visual impairments to navigate independently.

For those battling Alzheimer's, Memory Reboot becomes a beacon of hope. It facilitates memory reboot through advanced features such as face recognition, helping individuals recognize and remember their loved ones. The voice-assisted shortest path navigation ensures that those with Alzheimer's can wander outdoors safely, with family members monitoring their journey through the Neutrack website to prevent any direction loss.

Memory Reboot goes beyond its primary focus and extends its utility to drivers, travelers, and anyone seeking a personalized navigation solution. With highly customizable features, it serves as a handy tool for those in need of the shortest path option, GPS tracking, or voice-assisted personal assistance.

## Screenshot
### Website
The following is the display of the NeuTrack website.
![Screenshot from 2024-01-13 02-51-42](https://github.com/Sirund/neuTrack/assets/120204570/379bb58e-f936-490b-b0bd-43306477c308)

![Screenshot from 2024-01-13 02-48-53](https://github.com/Sirund/neuTrack/assets/120204570/9e4bc672-356c-4836-9f58-7540ae1f04ad)

### Prototype
Next is the prototype appearance of the NeuTrack glove.
![Screenshot from 2024-01-13 02-48-33](https://github.com/Sirund/neuTrack/assets/120204570/83dabb0e-111b-40d1-a033-f8f6f3103377)

![Screenshot from 2024-01-13 02-48-03](https://github.com/Sirund/neuTrack/assets/120204570/07b1559f-8b33-4b45-a2ff-ebea081bb8fa)

## Tutorial
### Object Detection
First go inside your virtual environment, then input this command to your terminal
```bash
git clone https://github.com/Sirund/neuTrack.git
cd neuTrack/Glove/object_detection
sh setup.sh
python3 detect.py --model efficientdet_lite0.tflite
```

### Face Recognition
Now you can setup your raspberry pi environment with following instruction from this website https://core-electronics.com.au/guides/face-identify-raspberry-pi/
if you want to create your own face model, input your photos to folder with your name inside the data folder. Then run command,
```bash
git clone https://github.com/Sirund/neuTrack.git
cd ~/neuTrack/Glove/face_recognition
python3 train_model.py
```
After that if you want to rocognize your face with the raspberry you can do this command,
```bash
cd ~/neuTrack/Glove/face_recognition
python3 facial_req.py
```

### Website
If you want to run the website make sure that you have npm in your laptop
```bash
git clone https://github.com/Sirund/neuTrack.git
cd ~/neuTrack/Web
npm install
npm run dev
```
