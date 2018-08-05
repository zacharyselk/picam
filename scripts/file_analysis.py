 # Performs analysis on a .timestamp.log file giving graphical and statistical information

import sys
import math
import matplotlib.pyplot as plt

try:
    import cv2
except:
    print('Warning! Cannot import cv2')


class plot:
    __slot__ = ('x_label', 'y_label')
    
    def __init__(self, x_axis, y_axis, color):
        self.draw_lines = [(x_axis, y_axis, color)]
        self.draw_bars = []
        #self.x_label = ''
        #self.y_label = ''

        
    def add_line(self, x_axis, y_axis, color):
        self.draw_lines.append((x_axis, y_axis, color))

    def get_draw_lines(self):
        return self.draw_lines

    
    def add_bar(self, value):
        self.draw_bars.append(value)

    def get_draw_bars(self):
        return self.draw_bars

        
                               
class fileAnalysis:
    def __init__(self, path_name):
        self.path_name = path_name
        self.timestamp_path = path_name + '.timestamp.log'
        self.tracking_path = path_name + '.tracking.log'
        self.timestamp_lines = []
        self.tracking_lines = []
        self.tracking = False
        self.framerate = 0
        self.total_time = 0
        self.time_difference = []
        self.standard_deviation = u''

        with open(self.timestamp_path, 'r') as f:
            self.timestamp_lines = f.readlines()
            
        # Check to see if the file exists
        try:
            with open(self.tracking_path, 'r') as f:
                # Ignoring the first line to match up the timestamps
                self.tracking_lines = f.readlines()[1:]
            self.tracking = True
        except:
            pass

        self.find_info()


    def find_time_differences(self):
        self.time_difference = []
        self.total_time = 0
        last_time = float(self.timestamp_lines[0])

        for timestamp in self.timestamp_lines[1:]:
            difference = float(timestamp) - last_time
            self.total_time += difference
            self.time_difference.append(difference)
            last_time = float(timestamp)
            

#     # Called by init to get info data        
#     def find_standard_deviation(self):
#         total = 0
#         prev_time = float(self.timestamp_lines[0]);
      
#         for line in self.timestamp_lines[1:]:
#             total += float(line) - prev_time
#             prev_time = float(line)
#         mean = total / (len(self.timestamp_lines)-1)

#         deviation_sum = 0
#         prev_time = float(self.timestamp_lines[0])

#         for line in self.timestamp_lines[1:]:
#             deviation_sum += (float(line)-prev_time-mean)**2
#             prev_time = float(line)

#         standard_deviation = deviation_sum / len(self.timestamp_lines)
#         (multiplier, units) = self.get_time_units(standard_deviation)
                             
#         standard_deviation *= multiplier
#         standard_deviation = math.sqrt(standard_deviation)
                             
#         self.standard_deviation = ('%f %s' % (standard_deviation, units))

    def find_framerate(self):
        self.framerate = 1 / ((self.total_time/1000) / len(self.time_difference))


    def find_standard_deviation(self):
        mean = self.total_time / len(self.time_difference)
        deviation_sum = 0

        for difference in self.time_difference:
            deviation_sum += (difference-mean)**2

#<<<<<<< HEAD
        standard_deviation = deviation_sum/len(self.time_difference)
        (multiplier, units) = self.get_time_units(standard_deviation)
        standard_deviation = math.sqrt(standard_deviation)
#=======
#        standard_deviation = math.sqrt(deviation_sum/len(self.time_difference))
#        (multiplier, units) = self.get_time_units(standard_deviation)
#>>>>>>> ac062d44c6d1448c4fd9be0cdbb957c6931aface
        standard_deviation *= multiplier

        self.standard_deviation = (standard_deviation, units)
    
#     # Called by init to get info data                
#     def find_framerate(self):
#         total_time = 0
#         prev_time = 0
#         for line in self.timestamp_lines:
#             # Move from msec to sec
#             time = float(line) / 1000.0
#             total_time += time - prev_time
#             prev_time = time
            
#<<<<<<< HEAD
#         self.length = total_time
#         ave = total_time / (len(self.timestamp_lines)-1)
#         self.framerate = 1.0/ave
#         self.find_standard_deviation()

    def find_info(self):
        self.find_time_differences()
        self.find_framerate()
        self.find_standard_deviation()
        print(self.get_mean_difference())
#=======
#        self.length = total_time
#        ave = total_time / (len(self.timestamp_lines)-1)
#        self.framerate = 1.0/ave
#        self.find_time_differences()
#        self.find_standard_deviation()        
#>>>>>>> ac062d44c6d1448c4fd9be0cdbb957c6931aface


    # Helper function, returns a normalized multiplier and time unit when given a
    #     num in ms
    def get_time_units(self, num):
        if num >= 3600000:
            multiplier = 1/3600000
            units = 'hr'
        elif num >= 60000:
            multiplier = 1/60000
            units = 'min'
        elif num > 1000:
            multiplier = 1/1000
            units = 'sec'
        elif num > 1:
            multiplier = 1
            units = 'ms'
        else:
            multiplier = 1000
            units = '\xB5s'
        return (multiplier, units)            
    
        
    def get_mean_difference(self):
        return self.total_time / len(self.time_difference)


    def get_standard_deviation(self):
        return self.standard_deviation[0]/1000


    # Displays simple information about the file
    def info(self):
        print('  Sec: %s' % str(self.total_time/1000))
        print('  Frames: %s' % str(len(self.timestamp_lines)-1))
        print('  Framerate: %s' % str(self.framerate))
        print('  Standard Deviation: %f %s' % self.standard_deviation)

        
    # Finds frames if a frame has deviated more than half the
    #     inverse of the framerate from the standard then determins
    #     whether a timeframe is missing a frame or has too many frames
    def dropped_frames(self):
        frames = len(self.timestamp_lines)-1
        list_of_frames = [[]*frames]
        INVERSE_FPS = 1.0/self.framerate
        
        for line in self.timestamp_lines:
            time = float(line) / 1000.0
            index = int(time/INVERSE_FPS + 0.5)
            while index >= len(list_of_frames):
                list_of_frames.append([])
            list_of_frames[index].append(time/INVERSE_FPS - index*INVERSE_FPS)

            dropped = 0
            extra = 0
            extra_count = 0
            for frame in list_of_frames:
                if len(frame) > 1:
                    extra += 1
                    extra_count += len(frame)
                elif len(frame) < 1:
                    dropped += 1

        print('Dropped: %i' % dropped)
        print('Extra: %i' % extra)

        # If it is balanced then no frames where dropped, they where just
        #     in a different timeframe
        if(extra_count == 2*dropped):
            print('Balanced')
        else:
            print('Unbalanced')


    def get_point(self, box):
        """Retruns the center point of a box
        
        Args:
            box: A tuple defined as (x0, y0, x1, y1) where (x0, y0) is the top
            left corner and (x1, y1) is the bottom right corner
        """
        box = box.split(',')
        for i in range(len(box)):
            box[i] = float(box[i])

        if box[0] is -1 and box[1] is -1 and box[2] is -1 and box[3] is -1:
            return 0
        return (box[0] + (box[2]-box[0])/2, box[1] + (box[3]-box[1])/2)

    def calc_dist(self, point0, point1):
        """Returns the euclidean distance between point0 and point1"""
        return math.sqrt((point0[0]-point1[0])**2 + (point0[1]-point1[1])**2)

    def plot_tracking(self):
        if self.tracking is False:
            print('Sorry, there was no tracking file found')
            return

        if len(self.timestamp_lines) != len(self.tracking_lines):
            print('Not equal')
            print(len(self.timestamp_lines))
            print(len(self.tracking_lines))
            return

        x = []  # The x value of all the points
        y = []  # The y value of all the points
        # The last timestamp
        #last_time = float(self.timestamp_lines[0])
        # The last center point
        last_point = self.get_point(self.tracking_lines[0])
        for i in range(len(self.tracking_lines)-1):
            point = self.get_point(self.tracking_lines[i+1])
            y.append(self.calc_dist(point, last_point))
            x.append(float(self.timestamp_lines[i+1])/1000)  # Convert to sec
            last_point = point
        
        p = plot(x, y, 'g')
        p.y_label = 'Distance (px)'
        p.x_label = 'Sec'
        
        return p

    def apply_tracking(self, write, display):
        # try:
        #     cap = cv2.VideoCapture(self.path_name)
        # except:
        try:
            path = self.path_name.split('.')
            path[-1] = 'mp4'
            path = '.'.join(path)
            cap = cv2.VideoCapture(path)
        except Exception as e:
            print('Error: %s' % e)
            print(self.path_name)
            return
        
        sleeping = False
        prev_box = None
        seconds_waited = 0
        #count = 0
        writer = None
        if write is not None:
            writer = cv2.VideoWriter(write, 0x00000021, 30, (640, 480), False)
        
        #while(cap.isOpened()):
        for i, line in enumerate(self.tracking_lines[:-1]):
            line = line.split(',')
            box = (int(line[0]), int(line[1]), int(line[2]), int(line[3]))
            try:
                buzz = int(line[4])
            except:
                pass
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.rectangle(gray, (box[0], box[1]),
                                 (box[2], box[3]), (255, 255, 255), 2)
            if prev_box == box:
                seconds_waited += self.time_difference[i] / 1000
            else:
                seconds_waited = 0

            prev_box = box
                
            msg = "Sleeping" if seconds_waited >= 20 else "Awake"
                    
            cv2.putText(gray, msg, (15,30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255,255,255), 3, 8)
            try:
                if buzz == 1:
                    cv2.putText(gray, 'Buzz', (15, 600), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (255, 255, 255), 3, 8)
            except:
                pass
            if display is True:
                cv2.imshow('frame', gray)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            if write is not None:
                writer.write(gray)
            #count += 1
            #if count > 1000:
            #    break

        if write is not None:
            writer.release()
        cap.release()
        cv2.destroyAllWindows()
                
    
    # Plots the framerate of each frame in relation to the last frame
    def plot_framerate(self):
        x = []
        y = []
        last_time = float(self.timestamp_lines[0])
        for line in self.timestamp_lines[1:]:
            cur_time = float(line) / 1000.0
            fps = 1.0/(cur_time - last_time)
            x.append(cur_time)
            y.append(fps)
            last_time = cur_time

        p = plot(x, y, 'go')
        p.y_label = 'Framerate'
        p.x_label = 'Time [sec]'

        return p
        

    # Plots how much the closes frame deviates from being on the target_fps
    def plot_deviation(self, target_framerate):
        hits_x = []     # A list of x values for each frame
        hits_y = []     # A list of y values for each frame
        dropped_x = []  # A list of x values for each dropped frame
        dropped_y = []  # A list of y values for each dropped frame
        extra_x = []    # A list of x values for each additional frame
        extra_y = []    # A list of y values for each additional frame
        
        # The inverse of the framerate, to give a timeframe for where a frame
        #     should be found
        time_gap = 1.0/float(target_framerate)
        correct_time = 0  # Where the frame should be found
        line_num = 0      # What line from the file is being used
        count = 0         # Counting the number of frames
        
        while(line_num < len(self.timestamp_lines)):
            time = float(self.timestamp_lines[line_num]) / 1000.0
            
            # Frame was either dropped or very delayed
            if time >= correct_time + time_gap:
                dropped_x.append(count)            
                # y value is set to time_gap so that extrenuous points
                #     don't lower the resolution on the usefull information
                #     when plotting            
                dropped_y.append(time_gap)
                
                # An extra frame was found in the previous period
                #     (usually from delayed frames)
            elif time <= correct_time - time_gap:
                extra_x.append(count)
                # y value is set to -time_gap so that extrenuous points
                #     don't lower the resolution on the usefull information
                #     when plotting
                extra_y.append(-time_gap)

                # Don't advance the time, because we are looking for
                #     a frame in this time period, and maybe the next
                #     frame is in it
                line_num += 1
                count += 1
                continue
        
            # The frame was found in the correct time period
            else:
                hits_x.append(count)
                hits_y.append(time - correct_time)
                line_num += 1
            
            count += 1               # Another frame is found
            correct_time += time_gap # Advance the timeframe


        multiplier = 1000000
        units = '\xB5s'
        if time_gap > 1:
            multiplier = 1
            units = 'sec'
        elif time_gap * 1000 > 1:
            multiplier = 1000
            units = 'ms'

        # Plotting everything
        p = plot(hits_x[1:], [i*multiplier for i in hits_y[1:]], 'go')
        p.add_line(dropped_x[1:], [i*multiplier for i in dropped_y[1:]], 'ro')
        p.add_line(extra_x[1:], [i*multiplier for i in extra_y[1:]], 'ro')
        p.y_label = 'Time Deviation from Expected [%s]' % units
        p.x_label = 'Frame'

        return p


    def plot_relative_deviation(self):
        return self.plot_deviation(self.framerate)

    def plot_timestamps(self):
        list_of_times = []
        x_axis = []
        (multiplier, units) = self.get_time_units(float(self.timestamp_lines[1]) - float(self.timestamp_lines[0]))
        last_time = float(self.timestamp_lines[0])*multiplier

        for i, timestamp in enumerate(self.timestamp_lines[1:]):
            list_of_times.append(float(timestamp)*multiplier - last_time)

            last_time = float(timestamp) * multiplier
            x_axis.append(i)

        p = plot(x_axis, list_of_times, 'g')
        p.y_label = units
        p.x_label = 'Timestamp'

        return p

    def plot_dropped_frames(self):
        count = 0
        list_of_times = []
        last_time = float(self.timestamp_lines[0])
        inverted_framerate = 1.0/self.framerate * 1000

        for timestamp in self.timestamp_lines[1:]:
            frames = int((float(timestamp)-last_time) / inverted_framerate)
            if frames > 1:
                count += frames-1
        
            last_time = float(timestamp)

        return count
