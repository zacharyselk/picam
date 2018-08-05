import matplotlib.pyplot as plt
from file_analysis import fileAnalysis


class evaluate(object):
    __slot__ = ('x_size', 'y_size', 'plot_style')
    def __init__(self, ts_path_name):
        if type(ts_path_name) != type([]):
            ts_path_name = [ts_path_name]

        self.file_path = ts_path_name
        self.files = []
        self.plot_style = 'vertical'
        self.x_size = 8
        self.y_size = 6

        for i in range(len(self.file_path)):
            self.files.append(fileAnalysis(self.file_path[i]))


    def plot(self, plot_data):
        # Get current size
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = self.x_size
        fig_size[1] = self.y_size
        plt.rcParams["figure.figsize"] = fig_size
        

        if len(plot_data) == 1:
            plt.title(self.file_path[0].split('/')[-1][:-3])
            plt.xlabel(plot_data[0].x_label)
            plt.ylabel(plot_data[0].y_label)
            plt.plot(*plot_data[0].get_draw_lines()[0])

            
        # Dont use for now
        elif len(plot_data) == -1:
            p, ((sub_plot1, sub_plot2), (sub_plot3, sub_plot4)) = plt.subplots(2, 2, sharex='col', sharey='row')
            p.subplots_adjust(hspace=0.25, wspace=0.25)

            sub_plot1.set_title(self.file_path[0].split('/')[-1][:-3])
            for line in plot_data[0].get_draw_lines():            
                sub_plot1.plot(*line)

            sub_plot2.set_title(self.file_path[1].split('/')[-1][:-3])
            for line in plot_data[1].get_draw_lines():
                sub_plot2.plot(*line)

            sub_plot3.set_title(self.file_path[2].split('/')[-1][:-3])
            for line in plot_data[2].get_draw_lines():
                sub_plot3.plot(*line)

            sub_plot4.set_title(self.file_path[3].split('/')[-1][:-3])
            for line in plot_data[3].get_draw_lines():
                sub_plot4.plot(*line)

        else:
            if self.plot_style == 'horizontal':
                p, sub_plots = plt.subplots(1, len(plot_data), sharey=True)
            else:
                p, sub_plots = plt.subplots(len(plot_data), sharex=True)

            p.subplots_adjust(hspace=0.25, wspace=0.25)
            for i in range(len(plot_data)):
                sub_plots[i].set_title(self.file_path[i].split('/')[-1][:-3])
                plt.xlabel(plot_data[i].x_label)
                plt.ylabel(plot_data[i].y_label)
                for line in plot_data[i].get_draw_lines():                    
                    sub_plots[i].plot(*line)

        plt.draw()
        plt.show()
        plt.close()
        print('\n')
        
            
    def info(self):
        for i, obj in enumerate(self.files):
            print(self.file_path[i].split('/')[-1][:-3])
            obj.info()
            print('\n')


    def dropped_frames(self):
        for obj in self.files:
            obj.dropped_frames()
            

    def plot_framerate(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_framerate())

        self.plot(plot_data)
    

    
    def plot_standards(self):
        mean_value = []
        deviations = []
        for obj in self.files:
            mean_value.append(obj.get_mean_difference())
            deviations.append(obj.get_standard_deviation())

        fig, ax = plt.subplots()
        bar = ax.bar(sorted(range(len(mean_value)), key=lambda x: mean_value[x]), 
                     mean_value, yerr=deviations)

        plt.draw()
        plt.show()
        plt.close()


    def plot_deviation(self, target_framerate):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_framerate(target_framerate))

        self.plot(plot_data)


    def plot_relative_deviation(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_relative_deviation())

        self.plot(plot_data)


    def plot_tracking(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_tracking())

        self.plot(plot_data)

    def apply_tracking(self, write=None, display=True):
        for obj in self.files:
            obj.apply_tracking(write, display)
        
    def plot_timestamps(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_timestamps())

        self.plot(plot_data)


    def plot_dropped_frames(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_dropped_frames())

        plt.bar([3,2,1], plot_data)
        plt.xticks([3,2,1], ('480p @ 120','720p @ 60','1080p @ 30'))
        plt.ylabel('Dropped Frames')
        plt.show()
        plt.close()

        
