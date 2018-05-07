#!/usr/bin/python

# Basic recording script for the picam

import sys
import picamera

if len(sys.argv) != 4:
    print("Usage error: %s length framerate file_name" % sys.argv[0])
    sys.exit

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = float(sys.argv[2])
camera.start_recording(sys.argv[3])
camera.wait_recording(float(sys.argv[1]))
camera.stop_recording()
