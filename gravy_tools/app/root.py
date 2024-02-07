import tkinter as tk
import tkinter.ttk as ttk

from .images import get_imagetk
from .widgets.map import MapWidget

def start_app():
    root = tk.Tk()
    root.geometry('1536x815')
    root.resizable(False, False)
    root.iconphoto(True, get_imagetk('logo.png'))
    root.title('Gravy-Tools')

    # TODO: add root.protocol WM_DELETE_WINDOW to save cache

    ttk.Separator(root, orient='vertical').pack(side='left', fill='y')

    MapWidget(root).pack(side='left')
    ttk.Separator(root, orient='vertical').pack(side='left', fill='y')

    root.mainloop()