# A custom stream that will write both the video from the picamera
#     as well as a file of the timestamps for each frame


import io
import time

class TSOutput(object):
    def __init__(self, camera, v_filename, ts_filename):
        self.camera = camera
        self.video_output_stream = None        
        if v_filename:
            self.video_output_stream = io.open(v_filename, 'wb')
            
        self.ts_output_stream = io.open(ts_filename, 'w')
        self.start_time = None


    def write(self, buf):
        if self.video_output_stream is not None:
            self.video_output_stream.write(buf)
        if not self.camera.frame.complete:
            print('Not Complete')
            
        if self.camera.frame.complete and self.camera.frame.timestamp:
            if self.start_time is None:
                self.start_time = self.camera.frame.timestamp
            self.ts_output_stream.write('%f\n' % ((self.camera.frame.timestamp - \
                                                   self.start_time) / 1000.0))


    def flush(self):
        if self.video_output_stream is not None:
            self.video_output_stream.flush()
        self.ts_output_stream.flush()


    def close(self):
        if self.video_output_stream is not None:        
            self.video_output_stream.close()
        self.ts_output_stream.close()
