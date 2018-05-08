# Performs analysis on a .ts file giving graphical and statistical information

import sys
import matplotlib.pyplot as plt


class fileEvaluation:
    def __init__(self, ts_path_name, target_fps=None):
        self.target_fps = target_fps
        self.file_path = ts_path_name
        self.lines = []
        self.framerate = 0
        self.standard_deviation = u''
        
        with open(self.file_path, 'r') as f:
            self.lines = f.readlines()
        self.find_framerate()


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
        
    
        units = 'ms'
        if standard_deviation < 1:
            units = '\xB5s'
            standard_deviation *= 1000.0
        elif standard_deviation >= 1000:
            units = 'sec'
            standard_deviation /= 1000.0
        
        self.standard_deviation = ('%f %s' % (standard_deviation, units))

        
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
        plt.plot(x, y, 'go')
        plt.ylabel('Framerate')
        plt.xlabel('Time [sec]')
        plt.show()
        plt.close()


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

        # Plotting everything
        plt.plot(hits_x[1:], [i*1000000 for i in hits_y[1:]], 'go')
        plt.plot(dropped_x[1:], [i*1000000 for i in dropped_y[1:]], 'ro')
        plt.plot(extra_x[1:], [i*1000000 for i in extra_y[1:]], 'ro')
        plt.ylabel('Time Deviation from Expected [\xB5s]')
        plt.xlabel('Frame')
        plt.show()
        plt.close()


    def plot_relative_deviation(self):
        self.plot_deviation(self.framerate)

    def plot_timestamps(self):
        list_of_times = []
        x_axis = []

        for i, timestamp in enumerate(self.lines):
            list_of_times.append(float(timestamp))
            x_axis.append(i)

        plt.plot(x_axis, list_of_times, 'g')
        plt.ylabel('ms')
        plt.xlabel('Timestamp')
        plt.show()
        plt.close()
