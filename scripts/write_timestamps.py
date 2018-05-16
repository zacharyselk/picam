#!/usr/bin/python3

# A quick script for writing video and timestamp file from the picamera
#     when passed: length framerate resolution file_extention

import sys
import picamera
from tsOutput import TSOutput


if len(sys.argv) < 5:
    print('Error: Invalid Usage\n{} length '.format(sys.argv[0]) +\
          'framerate resolution [additional_descriptors] file_format')
    sys.exit(1)

with picamera.PiCamera() as camera:
    if sys.argv[3][:4] == '480p':
        camera.resolution = (640, 480)
    elif sys.argv[3][:4] == '720p':
        camera.resolution = (1280, 720)
    elif sys.argv[3][:4] == '1080':
        camera.resolution = (1920, 1080)
    else:
        print('Error: Invalid Resolution')
        sys.exit(1)
        
    camera.framerate = float(sys.argv[2])
    filename = '../logs/' + sys.argv[1] + 'sec_' + sys.argv[2] +\
               'fps_' + sys.argv[3]
    

    for i in range(4, len(sys.argv)-1):
        filename += '_' + sys.argv[i]

    if sys.argv[-1][0] != '.':
        filename += '.'
    filename += sys.argv[-1]

    camera.start_recording(TSOutput(camera, '/media/pi/untitled/other/test.h264',
                                    filename+'.ts'),
                           format=sys.argv[-1])

    camera.wait_recording(float(sys.argv[1]))
    camera.stop_recording()
