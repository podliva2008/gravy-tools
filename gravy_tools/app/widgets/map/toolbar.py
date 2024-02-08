import os
import json

import tkinter as tk
import tkinter.ttk as ttk

from ...images import get_imagetk

class Toolbar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.maptype_combobox = ttk.Combobox(self, state='readonly')

        self.coords_entry = ttk.Entry(self, width=35)
        self.coords_entry.insert(0, '45.02783176031718, 38.98838186625211')

        icon_refresh = get_imagetk('icon_refresh.png')
        self.refresh_button = ttk.Button(self, image=icon_refresh)
        self.refresh_button.icon_refresh = icon_refresh

        icon_zoomout = get_imagetk('icon_zoom-out.png')
        self.downscale_button = ttk.Button(self, image=icon_zoomout)
        self.downscale_button.icon_zoomout = icon_zoomout

        icon_zoomin = get_imagetk('icon_zoom-in.png')
        self.upscale_button = ttk.Button(self, image=icon_zoomin)
        self.upscale_button.icon_zoomin = icon_zoomin

        self.maptype_combobox.pack(side='left', padx=10, pady=10)
        self.coords_entry.pack(side='left', padx=10, pady=10)
        self.refresh_button.pack(side='left', padx=10, pady=10)
        self.downscale_button.pack(side='left', padx=10, pady=10)
        self.upscale_button.pack(side='left', padx=10, pady=10)

        # Get maps tile servers and shape of globe tile server relies on
        try:
            config_folder = os.environ.get('CONFIG_DIR')
            maps_path = config_folder + '/maps.json'

            with open(maps_path, 'r') as file:
                json_string = file.read()
                self.maps_info = json.loads(json_string)
        except FileNotFoundError:
            # For those megaminds who decided to delete that file
            # Or if a file doesnt exist
            self.maps_info = [
                {
                    'ui_name': 'Яндекс схема',
                    'file_name': 'yandex_plain',
                    'tile_url': ('https://core-renderer-tiles.maps.yandex.'
                                 'net/tiles?l=map&x={}&y={}&z={}'),
                    'is_ellipsoid': True
                },
                {
                    'ui_name': 'Яндекс спутник',
                    'file_name': 'yandex_aerial',
                    'tile_url': ('https://core-sat.maps.yandex.net/'
                                 'tiles?l=sat&x={}&y={}&z={}'),
                    'is_ellipsoid': True
                }
            ]

            with open(maps_path, 'w') as file:
                json.dump(self.maps_info, file, indent=4, ensure_ascii=False)
        finally:
            self.maptype_combobox['values'] = [
                i['ui_name'] for i in self.maps_info
            ]