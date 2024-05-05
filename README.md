# NeuTrack

## Description
Introducing Memory Reboot, a groundbreaking solution designed to enhance the lives of visually impaired individuals and those affected by Alzheimer's, while revolutionizing navigation for drivers and travelers. Have you ever pondered the challenges faced by those surrounded by darkness or the sudden loss of memories, forgetting both loved ones and the way back home?

Memory Reboot addresses the inefficiency of traditional walking sticks for the visually impaired by providing real-time obstacle detection through cutting-edge text-to-speech computer vision and an ultrasonic rangefinder. This not only aids in obstacle avoidance but also offers crucial object information, empowering individuals with visual impairments to navigate independently.

For those battling Alzheimer's, Memory Reboot becomes a beacon of hope. It facilitates memory reboot through advanced features such as face recognition, helping individuals recognize and remember their loved ones. The voice-assisted shortest path navigation ensures that those with Alzheimer's can wander outdoors safely, with family members monitoring their journey through the Neutrack website to prevent any direction loss.

Memory Reboot goes beyond its primary focus and extends its utility to drivers, travelers, and anyone seeking a personalized navigation solution. With highly customizable features, it serves as a handy tool for those in need of the shortest path option, GPS tracking, or voice-assisted personal assistance.

## NeuTrack on Website
The following is the display of the NeuTrack website.
![Screenshot from 2024-01-13 02-51-42](https://github.com/Sirund/neuTrack/assets/120204570/379bb58e-f936-490b-b0bd-43306477c308)

![Screenshot from 2024-01-13 02-48-53](https://github.com/Sirund/neuTrack/assets/120204570/9e4bc672-356c-4836-9f58-7540ae1f04ad)

### Tutorial for NeuTrack Website
If you want to run the website for monitoring the glove you can run this command
```bash
git clone https://github.com/Sirund/neuTrack.git
cd ~/neuTrack/Web
python3 app.py
```
## NeuTrack on Mobile Version
The beginning of NeuTrack app development on Flutter. You can simply open this project on an IDE then connect it to an emulator.

### Getting Started

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.

## Prototype
Next is the prototype appearance of the NeuTrack glove V.01.
![Screenshot from 2024-01-13 02-48-33](https://github.com/Sirund/neuTrack/assets/120204570/83dabb0e-111b-40d1-a033-f8f6f3103377)

We utilize a camera to perceive objects in front of the user and an ultrasonic sensor to detect object distances, thus minimizing the computation required by the Raspberry Pi. This device also features face recognition to allow users to recognize family and close acquaintances nearby.

Here's the latest prototype of the NeuTrack Glove V.02.
![Top 100 Storyboard (5)](https://github.com/Sirund/neuTrack/assets/120204570/bfa75a7a-2779-4248-8666-2d09141e8b3f)

In this latest version, we have integrated NeuTrack with Gemini AI so that this tool can describe things in front of it. This tool can also be used as a personal assistant that can answer questions and provide directions to the user's intended destination.

We have redesigned our product for enhanced comfort and visual appeal when used by users. To facilitate ease of use, we have also added buttons and a microphone so that users can switch modes at will.

## NeuTrack AI Glove Installation Tutorial
This tutorial will guide you through the installation process of the NeuTrack AI Glove.

### Prerequisites:
- Raspberry Pi 3, 4, or 5 
- Memory card with Rasbian OS 32-bit, Debian Bookworm
- Fan
- GPS Neo 6m
- Camera
- Microphone
- Button
- Buzzer
- Ultrasonic

### Raspberry Pi GPIO Pinout:
Below is an overview of the GPIO pins for Raspberry Pi
![GPIO Pinout Diagram](https://github.com/Sirund/neuTrack/assets/120204570/dfba7d68-fc05-4084-888c-73b71fdbf526)

### Ultrasonic, Button and Buzzer Setup Guide
This guide will walk you through the process of setting up an Ultrasonic Sensor, Button, and Buzzer on your Raspberry Pi.

#### Connect the Ultrasonic Sensor to the Raspberry Pi:
| Raspberry Pi           |  Ultrasonic          |
|------------------------|----------------------|
| 5V (Pin 2 or 4)        | VCC                  |
| Ground (Pin 30)        | GND                  |
| GPIO 17                | Trig                 |
| GPIO 4                 | Echo                 |

#### Connect the Button to the Raspberry Pi:
| Raspberry Pi           |  Button              |
|------------------------|----------------------|
| GPIO 23                | One Leg              |
| Ground (Pin 39)        | Other Leg            |

#### Connect the Buzzer to the Raspberry Pi:
| Raspberry Pi           |  Ultrasonic          |
|------------------------|----------------------|
| 5V (Pin 2 or 4)        | Positive             |
| Ground (Pin 30)        | Negative             |

### GPS Setup Guide
This guide will walk you through the process of setting up a GPS module on your Raspberry Pi.

#### Hardware Connections
Here are the connections for the NEO-6M GPS module with the Raspberry Pi:
| Raspberry Pi           | NEO-6M GPS Module   |
|------------------------|----------------------|
| 5V (Pin 2 or 4)     | VCC       |
| Ground (Pin 6 or 9 or 14) | GND    |
| TX (GPIO 14 - UART0_TXD) | RX     |
| RX (GPIO 15 - UART0_RXD) | TX (Not required in our case)|

#### Get Data From GPS
Now here we need to modify few things. At first we need to edit the /boot/config.txt file. Now you need to open this file in any text editor. Here I am using nano:
```bash
sudo nano /boot/config.txt
```
At the end of the file add the follwing lines:
```bash
dtparam=spi=on
dtoverlay=pi3-disable-bt
core_freq=250
enable_uart=1
force_turbo=1
```
Now save this by typing ctrl +x, then type y and press enter.

Raspbian uses the UART as a serial console and so we need to turn off that functionality. To do so we need to change the /boot/cmdline.txt file. For safety before editing the file make a backup of that using the following command:
```bash
sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline_backup.txt
```
Now to edit that file open that in text editor:
```bash
sudo nano /boot/cmdline.txt
```
Replace the content with the follwing line (delete everything in it and write down the following content):
```bash
dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet splash plymouth.igno
```
Now save this by typing ctrl +x, then type y and press enter.
Now reboot pi using:
```bash
sudo reboot
```
Now, before we write the Python code to retrieve GPS data, we need to set up a few things again. By default, the Raspberry Pi uses the serial port for "console" login. So, if we intend to use the serial port to receive data from the GPS module, we need to disable the console login. In Raspberry Pi 3, there are two serial ports: serial0 and serial1. However, serial0 is mapped to GPIO pins 14 and 15. Therefore, we'll be using serial0. To identify which port is associated with serial0, use the following command:
```bash
ls -l /dev
```

There are two possible outputs:
- If your output looks like this:
![s1](https://github.com/Sirund/neuTrack/assets/120204570/0f7396e0-73d4-4edb-96b0-a0c1a421088f)

As you can see serial0 is linked with ttyAMA0. So to disable the console you need to use the follwing commands:
```bash
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
```

- But if your output looks like this:
![s2](https://github.com/Sirund/neuTrack/assets/120204570/be3f101f-f309-43be-9643-ab76e9edc3d3)

That means serial0 is linked with ttyS0. So to disable the console you need to use the follwing commands:
```bash
sudo systemctl stop serial-getty@ttyS0.service
sudo systemctl disable serial-getty@ttyS0.service
```
Now we need to install a python library:
```bash
pip install pynmea2
```
### Face Recognition Setup Guide
This guide will help you set up face recognition using Python and the `face_recognition` library.

To connect to the Raspberry Pi terminal, you have various options including VNC, SSH, or PuTTY. Open the terminal and execute each command by copying and pasting it into your Pi's terminal window. After pasting each command, press Enter and wait for it to complete before proceeding to the next one. If prompted with 'Do you want to continue? (y/n)', type 'Y' and then press Enter to proceed with the process.

```bash
sudo apt-get update

sudo apt-get upgrade

sudo apt install cmake build-essential pkg-config git

sudo apt install libjpeg-dev libtiff-dev libjasper-dev libpng-dev libwebp-dev libopenexr-dev

sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libdc1394-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev

sudo apt install libgtk-3-dev libqt5gui5 libqt5webkit5 libqt5test5 python3-pyqt5

sudo apt install libatlas-base-dev liblapacke-dev gfortran

sudo apt install libhdf5-dev libhdf5-103

sudo apt install python3-dev python3-pip python3-numpy
```

We must now expand the swapfile before running the next set of commands. To do this type and enter into the Terminal the following line.
```bash
sudo nano /etc/dphys-swapfile
```

The change the number on CONF_SWAPSIZE = 100 to CONF_SWAPSIZE=2048. Having done this press Ctrl-X, Y, and then Enter Key to save these changes. This change is only temporary and we will be changing it back. To have these changes affect anything we must restart the swapfile by entering the following command to the terminal. Then we will resume Terminal Commands as normal.
```bash
sudo systemctl restart dphys-swapfile

git clone https://github.com/opencv/opencv.git

git clone https://github.com/opencv/opencv_contrib.git

mkdir ~/opencv/build

cd ~/opencv/build

cmake -D CMAKE_BUILD_TYPE=RELEASE \

-D CMAKE_INSTALL_PREFIX=/usr/local \

-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \

-D ENABLE_NEON=ON \

-D ENABLE_VFPV3=ON \

-D BUILD_TESTS=OFF \

-D INSTALL_PYTHON_EXAMPLES=OFF \

-D OPENCV_ENABLE_NONFREE=ON \

-D CMAKE_SHARED_LINKER_FLAGS=-latomic \

-D BUILD_EXAMPLES=OFF ..

make -j$(nproc)
```

This | make | Command will take over an hour to install and there will be no indication of how much longer it will take. It may also freeze the monitor display. Be ultra patient and it will work. Once complete you are most of the way done. Then we will resume terminal commands.
```bash
sudo make install

sudo ldconfig

pip install face-recognition --no-cache-dir
```

This | pip install face-recognition| Command will take over 40 mins to install and there will be no indication of how much longer it will take. Be ultra patient and it will work. Once complete you are most of the way done. Then we will resume terminal commands.
```bash
pip install imutils
```

We must now return the swapfile before running the next set of commands. To do this type into Terminal this line.
```bash
sudo nano /etc/dphys-swapfile
```

The change the number on CONF_SWAPSIZE = 2048 to CONF_SWAPSIZE=100. Having done this press Ctrl-X, Y, and then Enter Key to save these changes. This returns the Swapfile to normal. To have these changes affect anything we must restart the swapfile by entering the following command to the terminal. Then we will resume terminal Commands as normal.
```bash
sudo systemctl restart dphys-swapfile
```

### Speech Recognition Setup Guide for Raspberry Pi

This guide will walk you through the process of setting up speech recognition on your Raspberry Pi using Python.
```bash
sudo apt-get install portaudio19-dev python3-all-dev && sudo pip install pyaudio
sudo apt install flac
sudo pip install SpeechRecognition
```

### Gemini Pro Setup Guide

This guide will walk you through the process of setting up Gemini Pro and Gemini Pro Vision on your system.
```bash
pip install -U google-generativeai
```

### Getting Started
Open the terminal and use the following command:
```bash
git clone https://github.com/Sirund/neuTrack.git
cd neuTrack/pi5
```

to run the code you can use this command:
```bash
python3 main.py
```



