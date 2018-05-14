#!/usr/bin/python3

# A custom class for writing both the video feed, as well as
#     writing the timestamps given by the picam, to files

import io
import sys
import time
import picamera

import socketStream as socket

byte_count = 0

class TSOutput(object):
    def __init__(self, camera, v_filename, ts_filename, local_time_filename):
        self.camera = camera
        #self.video_output_stream = io.open(v_filename, 'wb')
        #self.video_output_stream = io.open('/dev/null', 'wb')
        #self.video_output_stream = socket.InetStream(s=None)
        #self.video_output_stream.connect('142.66.96.154', 1122)
        self.msg_flag = False
        
        self.ts_output_stream = io.open(ts_filename, 'w')
        self.local_time_output_stream = io.open(local_time_filename, 'w')
        self.start_time = None

    def size_of(self, string):
        return len(str(string).encode('utf-8'))

    def write(self, buf):
        # Send the expected frame size to the server
        '''if not self.msg_flag:
            print(sys.getsizeof(buf))
            self.video_output_stream.send_len(sys.getsizeof(buf))
            self.video_output_stream.set_msg_len(sys.getsizeof(buf))
            self.msg_flag = True
        '''
        # Frames that are too small?
        #if sys.getsizeof(buf) < 500:
        #    print(buf)
        #self.video_output_stream.write(buf)
        if not self.camera.frame.complete:
            print('Not Complete')
            
        if self.camera.frame.complete and self.camera.frame.timestamp:
            if self.start_time is None:
                self.start_time = self.camera.frame.timestamp
            self.ts_output_stream.write('%f\n' % ((self.camera.frame.timestamp - \
                                                   self.start_time) / 1000.0))
            #self.local_time_output_stream.write(str(time.time()))

    def flush(self):
        #self.video_output_stream.flush()
        self.ts_output_stream.flush()
        #self.local_time_output_stream.flush()

    def close(self):
        #self.video_output_stream.close()
        self.ts_output_stream.close()
        #self.local_time_output_stream.close()



with picamera.PiCamera() as camera:
    if sys.argv[3][:4] == '480p':
        camera.resolution = (640, 480)
    elif sys.argv[3][:4] == '720p':
        camera.resolution = (1280, 720)
    elif sys.argv[3][:4] == '1080':
        camera.resolution = (1920, 1080)
        
    camera.framerate = float(sys.argv[2])
    filename = '../logs/' + str(sys.argv[1]) + 'sec_' + str(sys.argv[2]) +\
               'fps_' + str(sys.argv[3]) + '.' + str(sys.argv[4])
    camera.start_recording(TSOutput(camera, '/media/pi/untitled/other/test.h264',
                                    filename+'.ts', filename+'.lt'),
                           format=sys.argv[4])

    camera.wait_recording(float(sys.argv[1]))
    camera.stop_recording()
    #print(byte_count)
