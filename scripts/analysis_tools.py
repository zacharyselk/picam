import matplotlib.pyplot as plt
from file_analysis import fileAnalysis


class evaluate:
    def __init__(self, ts_path_name):
        if type(ts_path_name) != type([]):
            ts_path_name = [ts_path_name]

        self.file_path = ts_path_name
        self.files = []
        self.plot_style = 'vertical'

        for i in range(len(self.file_paths)):
            self.files.append(fileAnalysis(self.file_path[i]))


    def style(self, style):
        self.plot_style = style

            
    def plot(plot_data):
        if len(plot_data) == 1:
            plt.plot(*plot_data[0].get_draw_lines())
            plt.xlabel(plot_data[0].x_label)
            
        elif len(plot_data) == 4:
            p, ((sub_plot1, sub_plot2), (sub_plot3, sub_plot4)) = plt.subpots(2, 2, sharex='col', sharey='row')
            sub_plot1.plot(*plot_data[0])
            sub_plot2.plot(*plot_data[1])
            sub_plot3.plot(*plot_data[2])
            sub_plot4.plot(*plot_data[3])

        else:
            p, sub_plots = plt.subplots(len(plot_data))
            for i in range(len(plot_data)):
                sub_plots[i].title(self.file_path[i].split('/')[-1])
                sub_plots[i].plot(*plot_data[i])

        plt.show()
        plt.close()
        
            
    def info(self):
        for i, obj in enumerate(self.files):
            print(self.file_path[i])
            ojb.info()
            print('\n')


    def plot_framerate(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_framerate())

        self.plot(plot_data)
    

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


    def plot_timestamps(self):
        plot_data = []
        for obj in self.files:
            plot_data.append(obj.plot_timestamps())

        self.plot(plot_data)
