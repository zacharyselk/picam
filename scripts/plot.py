class coord(Object):
    __slots__ = ('x', 'y')

class plot:
    def __init__(self, x_axis, y_axis, color):
        self.draw_lines = [(x_axis, y_axis, color)]


    def add_line(self, x_axis, y_axis, color):
        self.draw_lines.append((x_axis, y_axis, color)
