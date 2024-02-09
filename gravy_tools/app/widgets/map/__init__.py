import tkinter as tk
import threading
import queue
import time

from PIL import Image, ImageTk

from .selections_canvas import PolygonCanvas
from .toolbar import Toolbar
from ...utils import Tile, fetch_tile
from ...images import get_imagetk

class MapWidget(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.scale = tk.IntVar(self, 19)

        self.polygon_canvas = PolygonCanvas(
            self, width=768, height=768, cursor='tcross'
            )
        self.toolbar = Toolbar(self)

        self.polygon_canvas.pack()
        self.toolbar.pack()
        
        self.toolbar.maptype_combobox.set(
            self.toolbar.maptype_combobox['values'][0]
            )

        # This makes it easier to call it from button
        update_map = lambda _ = None: threading.Thread(
            target=self.update_map
            ).start()

        self.toolbar.refresh_button['command'] = update_map
        self.toolbar.upscale_button['command'] = self.add_scale
        self.toolbar.downscale_button['command'] = self.subtract_scale
        self.toolbar.maptype_combobox.bind(
            '<<ComboboxSelected>>', self.get_map_info
        )

        self.get_map_info()
        update_map()


    def get_map_info(self, _ = None):
        for index, map_info in enumerate(self.toolbar.maps_info):
            if (
                map_info['ui_name'] == self.toolbar.maptype_combobox.get()
                or index == -1
            ):
                self.map_info = map_info
                self.tile_name, self.tile_url, self.is_ellipsoid = (
                    self.map_info['file_name'],
                    self.map_info['tile_url'],
                    self.map_info['is_ellipsoid']
                    )
                break


    def add_scale(self):
        curr_scale = self.scale.get()
        if 0 <= curr_scale + 1 <= 20:
            self.scale.set(curr_scale + 1)
            threading.Thread(target=self.update_map).start()


    def subtract_scale(self):
        curr_scale = self.scale.get()
        if 0 <= curr_scale - 1 <= 20:
            self.scale.set(curr_scale - 1)
            threading.Thread(target=self.update_map).start()


    def update_map(self):
        """Update map tiles on a polygon canvas"""

        # This is done to prevent user from creating multiple threads
        self.toolbar.refresh_button['state'] = 'disabled'
        self.toolbar.downscale_button['state'] = 'disabled'
        self.toolbar.upscale_button['state'] = 'disabled'

        coord_pair = self.toolbar.coords_entry.get()
        scale = self.scale.get()

        center_tile = Tile(coord_pair, scale, self.is_ellipsoid)

        self.center_calc_num = (center_tile.calc_x, center_tile.calc_y)
        center_img_x, center_img_y = (center_tile.img_x, center_tile.img_y)
        offset_x, offset_y = center_tile.offset_x, center_tile.offset_y

        self.polygon_canvas.delete('all')

        loader_icon = get_imagetk('icon_loader.png')
        self.polygon_canvas.create_image(
            256, 256, anchor='nw', image=loader_icon
            )

        # 5 tiles = 256 x 5 pixels = 1280 pixels
        map_pilimage = Image.new(
            mode='RGBA', size=(1280, 1280), color=(0, 0, 0, 0)
            )
        for x in range(-2, 3):
            tile_img_x = center_img_x + x
            for y in range(-2, 3):
                tile_img_y = center_img_y + y

                tile_pilimage = fetch_tile(
                    self.tile_name, self.tile_url,
                    (tile_img_x, tile_img_y), scale
                    )
                
                map_pilimage.paste(
                    im=tile_pilimage,
                    box=((256 * (x+2) - offset_x), (256 * (y+2) - offset_y))
                    )
                self.map_photoimage = ImageTk.PhotoImage(map_pilimage)

        self.polygon_canvas.delete('all')
        self.polygon_canvas.create_image(
            -256, -256, anchor='nw', image=self.map_photoimage
        )

        self.toolbar.refresh_button['state'] = 'enabled'
        self.toolbar.downscale_button['state'] = 'enabled'
        self.toolbar.upscale_button['state'] = 'enabled'
