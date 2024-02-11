import tkinter as tk
import math

class SelectionsCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)

        self.selection_geocoords = {}  # TODO: implement pixel <-> geo convert

    def add_selection(self, selection_type: str, tag: str, color: str):
        if selection_type == 'poly':
            self.create_polygon(
                __coords=[], width=2, outline=color, fill='', tags=[tag]
            )
        elif selection_type == 'lines':
            self.create_line(
                __coords=[], width=2, fill=color, arrow='last', tags=[tag]
            )
        elif selection_type == 'bezier':
            self.create_line(
                __coords=[], width=2, fill=color,
                arrow='last', smooth=True, tags=[tag]
            )
        else:
            raise Exception('Неверный тип выделения')
        
    def start_editing(self, selection_type: str, tag: str):
        points = self.coords(tag)

        if selection_type == 'poly':
            self.create_polygon(
                __coords=points, width=2, outline='red',
                fill='', tags=['temp']
            )
        elif selection_type == 'lines':
            self.create_line(
                __coords=points, width=2, fill='red',
                arrow='last', tags=['temp']
            )
        elif selection_type == 'bezier':
            self.create_line(
                __coords=points, width=2, fill='red',
                arrow='last', smooth=True, tags=['temp']
            )
        else:
            raise Exception('Неверный тип выделения')
        
        self.bind(
            '<Motion>', lambda event: self.temp_update_points(tag, event)
            )
        self.bind(
            '<ButtonRelease-1', lambda event: self.add_point(tag, event)
            )
        self.bind(
            '<ButtonRelease-2>', lambda _: self.delete_point(tag)
        )
        self.bind(
            '<ButtonRelease-3>', lambda _: self.end_editing()
        )

    def end_editing(self):
        self.unbind('<Motion>')
        self.unbind('<ButtonRelease-1>')
        self.unbind('<ButtonRelease-2>')
        self.unbind('<ButtonRelease-3>')

        self.delete('temp')

    def start_moving(self, tag: str):
        self.bind(
            '<Motion>', lambda event: self.drag_selection(tag, event)
            )
        self.bind(
            '<MouseWheel>', lambda event: self.rotate_selection(tag, event)
            )
        self.bind(
            '<ButtonRelease-3>', lambda _: self.end_editing()
        )

    def end_moving(self):
        self.unbind('<Motion>')
        self.unbind('<MouseWheel>')
        self.unbind('<ButtonRelease-3>')

    def drag_selection(self, tag: str, event: tk.Event):
        points = self.coords(tag)
        first_point = points[0]

        x_diff = first_point[0] - event.x
        y_diff = first_point[1] - event.y

        dragged_points = []
        for point in points:
            new_x = point[0] + x_diff
            new_y = point[1] + y_diff

            dragged_points.append((new_x, new_y))
        
        self.itemconfig(tag, __coords = dragged_points)

    def rotate_selection(self, tag: str, event: tk.Event):
        angle = event.delta / 120
        radian = math.radians(angle)

        points = self.coords(tag) 
        center_point = points[0]

        rotated_points = []
        for point in points:
            old_x = point[0] - center_point[0]
            old_y = point[1] - center_point[1]

            new_x = old_x * math.cos(radian) - old_y * math.cos(radian)
            new_y = old_x * math.cos(radian) + old_y * math.cos(radian)

            rotated_points.append((new_x, new_y))
        
        self.itemconfig(tag, __coords = rotated_points)

    def add_point(self, tag: str, event: tk.Event):
        points = self.coords(tag)
        points.append((event.x, event.y))
        self.itemconfig(tag, __coords = points)

    def delete_point(self, tag: str):
        points = self.coords(tag)
        del points[-1]
        self.itemconfig(tag, __coords = points)

    def temp_update_points(self, tag: str, event: tk.Event):
        points = self.coords(tag)
        points.append((event.x, event.y))
        self.itemconfig('temp', __coords = points)