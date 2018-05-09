# Performs analysis on a .ts file giving graphical and statistical information

import sys
import math
import matplotlib.pyplot as plt


class plot:
    __slot__ = ('x_label', 'y_label')
    
    def __init__(self, x_axis, y_axis, color):
        self.draw_lines = [(x_axis, y_axis, color)]
        #self.x_label = ''
        #self.y_label = ''

    def add_line(self, x_axis, y_axis, color):
        self.draw_lines.append((x_axis, y_axis, color))

    '''
    def x_label(self, label):
        self.x_label = label


    def y_label(self, label):
        self.y_label = label

    '''
    def get_draw_lines(self):
        return self.draw_lines

        
                               
class fileAnalysis:
    def __init__(self, ts_path_name):
        self.file_path = ts_path_name
        self.lines = []
        self.framerate = 0
        self.standard_deviation = u''
        
        with open(self.file_path, 'r') as f:
            self.lines = f.readlines()
        self.find_framerate()

        
    # Called by init to get info data        
    def find_standard_deviation(self):
        total = 0
        prev_time = 0;
        
        for line in self.lines:
            total += float(line) - prev_time
            prev_time = float(line)
        mean = total / len(self.lines)

        deviation_sum = 0
        prev_time = 0

        for line in self.lines:
            deviation_sum += (float(line)-prev_time-mean)**2
            prev_time = float(line)
        standard_deviation = deviation_sum / len(self.lines)
        (multiplier, units) = self.get_time_units(standard_deviation)
                               
        standard_deviation *= multiplier
        standard_deviation = math.sqrt(standard_deviation)
                               
        self.standard_deviation = ('%f %s' % (standard_deviation, units))

            # Called by init to get info data                
    def find_framerate(self):
        total_time = 0
        prev_time = 0
        for line in self.lines:
            # Move from msec to sec
            time = float(line) / 1000.0
            total_time += time - prev_time
            prev_time = time
            
        self.length = total_time
        ave = total_time / (len(self.lines)-1)
        self.framerate = 1.0/ave
        self.find_standard_deviation()        


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

        
    # Displays simple information about the file
    def info(self):
        print('Sec: %s' % str(self.length))
        print('Frames: %s' % str(len(self.lines)-1))
        print('Framerate: %s' % str(self.framerate))
        print('Standard Deviation: %s' % self.standard_deviation)

        
    # Finds frames if a frame has deviated more than half the
    #     inverse of the framerate from the standard then determins
    #     whether a timeframe is missing a frame or has too many frames
    def dropped_frames(self):
        frames = len(self.lines)-1
        list_of_frames = [[]*frames]
        INVERSE_FPS = 1.0/self.framerate
        
        for line in self.lines:
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


    # Plots the framerate of each frame in relation to the last frame
    def plot_framerate(self):
        x = []
        y = []
        last_time = float(self.lines[0])
        for line in self.lines[1:]:
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
        
        while(line_num < len(self.lines)):
            time = float(self.lines[line_num]) / 1000.0
            
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
        (multiplier, units) = self.get_time_units(float(self.lines[1]) - float(self.lines[0]))
        last_time = float(self.lines[0])*multiplier

        for i, timestamp in enumerate(self.lines[1:]):
            list_of_times.append(float(timestamp) * multiplier - last_time)
            last_time = float(timestamp) * multiplier
            x_axis.append(i)

        p = plot(x_axis, list_of_times, 'g')
        p.y_label = units
        p.x_label = 'Timestamp'

        return p
