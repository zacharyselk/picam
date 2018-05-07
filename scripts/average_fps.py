#!/usr/bin/python

# Performs analysis on a .ts file giving graphical and statistical information

import sys
import matplotlib.pyplot as plt


def main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(len(sys.argv))
        print("Usage Error: %s filename" % sys.argv[0])
        sys.exit
        
    with open(sys.argv[-1], 'r') as f:
        lines = f.readlines()
        sum = 0
        prev_time = 0
        for line in lines:
            # Move from msec to sec
            time = float(line) / 1000.0
            sum += time - prev_time
            prev_time = time
            
        # How far from correct point
        if len(sys.argv) > 2:
            plot_deviation(sys.argv[1])
        

        ave = sum / (len(lines)-1)
        fps = 1.0/ave
        #plot_deviation(fps, lines)
        print('Sec: %s' % str(sum))
        print('Frames: %s' % str(len(lines)-1))
        print('FPS: %s' % str(fps))
        find_dropped_frames(fps, lines)
        plot_current_fps(lines)


# Finds frames if a frame has deviated more than half the
#     inverse of the framerate from the standard then determins
#     whether a timeframe is missing a frame or has too many frames
def find_dropped_frames(fps, lines):
    frames = len(lines)-1
    list_of_frames = [[]*frames]
    INVERSE_FPS = 1.0/fps

    for line in lines:
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
def plot_current_fps(lines):
    x = []
    y = []
    last_time = float(lines[0])
    for line in lines[1:]:
        cur_time = float(line) / 1000.0
        fps = 1.0/(cur_time - last_time)
        x.append(cur_time)
        y.append(fps)
        last_time = cur_time
    plt.plot(x, y, 'go')
    plt.show()

    
# Plots how much the closes frame deviates from being on the target_fps
def plot_deviation(target_fps, lines):
    hits_x = []     # A list of x values for each frame
    hits_y = []     # A list of y values for each frame
    dropped_x = []  # A list of x values for each dropped frame
    dropped_y = []  # A list of y values for each dropped frame
    extra_x = []    # A list of x values for each additional frame
    extra_y = []    # A list of y values for each additional frame

    # The inverse of the framerate, to give a timeframe for where a frame
    #     should be found
    time_gap = 1.0/float(target_fps)
    correct_time = 0  # Where the frame should be found
    line_num = 0      # What line from the file is being used
    count = 0         # Counting the number of frames
    
    while(line_num < len(lines)):
        time = float(lines[line_num]) / 1000.0

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
    plt.plot(hits_x[1:], hits_y[1:], 'go')
    plt.plot(dropped_x[1:], dropped_y[1:], 'ro')
    plt.plot(extra_x[1:], extra_y[1:], 'ro')
    plt.ylabel('Time Deviation from Expected')
    plt.xlabel('Frame')
    plt.show()
    plt.close()

    
if __name__ == ' __main__':
    main()
