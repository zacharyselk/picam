"""Performs analysis on a .timestamp.log file giving graphical and
   statistical information

   Author: Zachary Selk <zrselk@gmail.com>
   Github: www.github.com/zacharyselk
   Date  : June 2018

  Style-Guide: https://www.github.com/google/styleguide/blob/gh-pages/pyguide.md
"""

import io
import sys
import math
import matplotlib.pyplot as plt

try:
    import cv2
except:
    print('Warning! Cannot import cv2')


class Plot:
    """Plots data in a graph.

       Args:
           plot_data: An matplotlib object containing the data to be plotted.

       Attributes:
           x_label: Label for the x-axis of the graph.
           y_label: Label for the y-axis of the graph.
    """
    __slots__ = ('x_label', 'y_label', 'draw_lines', 'draw_bars')

    def __init__(self, x_axis, y_axis, color):
        self.draw_lines = [(x_axis, y_axis, color)]
        self.draw_bars = []


    def add_line(self, x_axis, y_axis, color):
        """Adds a line to be drawn."""
        self.draw_lines.append((x_axis, y_axis, color))


    def get_draw_lines(self):
        """Returns the lines to be drawn."""
        return self.draw_lines


    def add_bar(self, value):
        """Adds a bar to be drawn."""
        self.draw_bars.append(value)


    def get_draw_bars(self):
        """Returns the bars to be drawn."""
        return self.draw_bars


class FileAnalysis:
    """Plots data in a graph.

        Args:
            path_name: The path to the video file.

       Attributes:
            path_name: The path to the video file.
            timestamp_path: The path to the timestamp file.
            tracking_path: The path to the tracking data file.
            timestamp_lines: List of timestamps.
            tracking_lines: List of tracking lines.
            tracking: Whether or not tracking is to be applied.
            framerate: Framerate of video.
            total_time: The duration of video.
            time_difference: List of time difference between 
            subsequent timestamps
            standard_deviation: The standard deviation of the framerate.
    """
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

        with open(self.timestamp_path, 'r') as timestamp_file:
            self.timestamp_lines = timestamp_file.readlines()

        # Check to see if the file exists
        try:
            with open(self.tracking_path, 'r') as tracking_file:
                # Ignoring the first line to match up the timestamps
                self.tracking_lines = tracking_file.readlines()[1:]
            self.tracking = True
        except:
            pass

        self.find_info()


    def find_time_differences(self):
        """Finds the time differences between 2 subsequent timestamps in order
           to find framerate.
        """
        self.time_difference = []
        self.total_time = 0
        last_time = float(self.timestamp_lines[0])

        for timestamp in self.timestamp_lines[1:]:
            difference = float(timestamp) - last_time
            self.total_time += difference
            self.time_difference.append(difference)
            last_time = float(timestamp)


    def find_framerate(self):
        """Finds the framerate of the video using time differences."""
        self.framerate = 1 / ((self.total_time/1000) /
                              len(self.time_difference))


    def find_standard_deviation(self):
        """Finds the standard deviation of the time differences"""
        mean = self.total_time / len(self.time_difference)
        deviation_sum = 0
        for difference in self.time_difference:
            deviation_sum += (difference - mean)**2

        standard_deviation = deviation_sum/len(self.time_difference)
        (multiplier, units) = self.get_time_units(standard_deviation)
        standard_deviation = math.sqrt(standard_deviation)
        standard_deviation *= multiplier
        self.standard_deviation = (standard_deviation, units)


    def find_info(self):
        """Computes useful analysis data."""
        self.find_time_differences()
        self.find_framerate()
        self.find_standard_deviation()


    def get_time_units(self, num):
        """returns time measurement units and its corresponding multiplier."""
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
        """Returns the mean difference"""
        return self.total_time / len(self.time_difference)


    def get_standard_deviation(self):
        """Returns the standard deviation difference"""
        return self.standard_deviation[0]/1000


    def info(self):
        """Displays simple information about the file."""
        print('  Sec: %s' % str(self.total_time/1000))
        print('  Frames: %s' % str(len(self.timestamp_lines)-1))
        print('  Framerate: %s' % str(self.framerate))
        print('  Standard Deviation: %f %s' % self.standard_deviation)


    def dropped_frames(self):
        """Finds frames if a frame has deviated more than half the
           inverse of the framerate from the standard then determines
           whether a timeframe is missing a frame or has too many frames.
        """
        frames = len(self.timestamp_lines)-1
        list_of_frames = [[]*frames]
        inverse_fps = 1.0/self.framerate

        for line in self.timestamp_lines:
            time = float(line) / 1000.0
            index = int(time/inverse_fps + 0.5)
            while index >= len(list_of_frames):
                list_of_frames.append([])
            list_of_frames[index].append(time/inverse_fps - index*inverse_fps)

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
        if extra_count == 2*dropped:
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
        for i in enumerate(box):
            box[i] = float(box[i])

        if box[0] is -1 and box[1] is -1 and box[2] is -1 and box[3] is -1:
            return 0
        return (box[0] + (box[2]-box[0])/2, box[1] + (box[3]-box[1])/2)


    def calc_dist(self, point0, point1):
        """Returns the euclidean distance between point0 and point1."""
        return math.sqrt((point0[0]-point1[0])**2 + (point0[1]-point1[1])**2)


    def plot_tracking(self):
        """Plots the tracking info from the tracking file"""
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
        """Displays the video feed with the tracking and sleep data overlayed.

           Args:
              write: The video to be written.
              display: Whether or not to display the video.
        """
        try:
            path = self.path_name.split('.')
            path[-1] = 'mp4'
            path = '.'.join(path)
            cap = cv2.VideoCapture(path)
        except Exception as e:
            print('Error: %s' % e)
            print(self.path_name)
            return

        path = '/'.join(self.path_name.split('/')[:-1]) + '/'
        sleep_writer = io.open(path + '__TMP__.sleeping.log', 'w')
        sleeping = False
        prev_box = None
        seconds_waited = 0
        #count = 0
        writer = None
        if write is not None:
            writer = cv2.VideoWriter(write, 0x00000021, 30, (640, 480), False)

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

            msg = 'Awake'
            if seconds_waited >= 20:
                msg = 'Sleeping'
                sleep_writer.write(u'1\n')
            else:
                sleep_writer.write(u'0\n')

            cv2.putText(gray, msg, (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 3, 8)
            try:
                if buzz == 1:
                    cv2.putText(gray, 'Buzz', (15, 600),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 255, 255), 3, 8)
            except:
                pass
            if display is True:
                cv2.imshow('frame', gray)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            if write is not None:
                writer.write(gray)

        if write is not None:
            writer.release()
        sleep_writer.close()
        cap.release()
        cv2.destroyAllWindows()


    def plot_framerate(self):
        """Plots the framerate of each frame in relation to the last frame."""
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


    def plot_deviation(self, target_framerate):
        """Plots how much the actual framerate deviates from being on
           the target_fps.

           Args:
              target_framerate: The framerate we expect or wish to 
              be capturing at.
        """
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

        while line_num < len(self.timestamp_lines):
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
        """Plots the relative deviation in a graph."""
        return self.plot_deviation(self.framerate)


    def plot_timestamps(self):
        """Plots the timestamps in a graph."""
        list_of_times = []
        x_axis = []
        (multiplier, units) = \
        self.get_time_units(float(self.timestamp_lines[1]) - \
                            float(self.timestamp_lines[0]))

        last_time = float(self.timestamp_lines[0]) * multiplier

        for i, timestamp in enumerate(self.timestamp_lines[1:]):
            list_of_times.append(float(timestamp) * multiplier - last_time)

            last_time = float(timestamp) * multiplier
            x_axis.append(i)

        p = plot(x_axis, list_of_times, 'g')
        p.y_label = units
        p.x_label = 'Timestamp'

        return p


    def plot_dropped_frames(self):
        """Plots the ammount of dropped frames in a graph."""
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
