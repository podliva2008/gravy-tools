import tkinter as tk

class SelectionsCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)

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

    def add_point(self, tag: str, event: tk.Event):
        points = self.coords(tag)
        points.append((event.x, event.y))
        self.itemconfig(tag, __coords = points)

    def delete_point(self, tag: str):
        points = self.coords(tag)
        del points[-1]
        self.itemconfig(tag, __coords = points)

    def edit_preview(self, tag: str, event: tk.Event):
        points = self.coords(tag)
        points.append((event.x, event.y))
        self.itemconfig('temp', __coords = points)