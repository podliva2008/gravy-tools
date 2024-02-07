__all__ = ['Tile', 'cache_tile', 'fetch_tile']

import os
import io
import math

from PIL import Image, ImageTk
import requests

from ..images import get_pilimage

class Tile:
    def __init__(self, coord_pair: str, scale: int, is_ellipsoid: bool):
        lat, lon = [float(i) for i in coord_pair.split(', ')]
        self.z = scale

        # Calculating tile number for the spherical projection
        # Those values should be used during calculations
        # https://clck.ru/37BGai
        s_tile_x = math.floor((lon + 180) / 360 * 2 ** self.z)
        s_tile_y = math.floor(
            (
                1 - math.log(
                    math.tan(lat * math.pi / 180) +
                    1 / math.cos(lat * math.pi / 180)
                ) / math.pi
            ) * 2 ** (self.z - 1)
            )

        if is_ellipsoid:
            # We will use spherical tile number and ellipsoidal tile number
            # to calculate the offset for the ellipsoidal tile to match
            # a spherical one based on geographical coordinates of those
            # https://clck.ru/37RLnz

            # Calculating earth compression on ellipsoid projection
            RADIUS_A = 6378137
            RADIUS_B = 6356752
            y_compr = math.sqrt((RADIUS_A ** 2) - (RADIUS_B ** 2)) / RADIUS_A

            # Calculating coordinates of upper-left corner of a tile
            s_tile_lon = s_tile_x / (2 ** self.z) * 360 - 180
            s_tile_lat = math.atan(
                math.sinh(math.pi - s_tile_y / (2 ** self.z) * (math.pi * 2))
                ) * 180 / math.pi

            # Latitude is in degrees, so convert it to radians
            tile_lat_radians = math.radians(s_tile_lat)

            # Honestly idk what m2 means but it is very importanté!!!!!
            m2 = math.log(
                (1 + math.sin(tile_lat_radians)) /
                (1 - math.sin(tile_lat_radians))
                ) / 2 - y_compr * math.log(
                    (1 + y_compr * math.sin(tile_lat_radians)) /
                    (1 - y_compr * math.sin(tile_lat_radians))
                    ) / 2

            # Calculate the tile number for the
            e_tile_x = math.floor((s_tile_lon + 180) / 360 * (2 ** self.z))
            e_tile_y = math.floor(
                (2 ** self.z) / 2 - m2 * (2 ** self.z) / 2 / math.pi
                )
            
            # And calculate offset of the ellipsoidal tile relative to
            # spherical tile
            self.offset_x = math.floor(
                ((s_tile_lon + 180) / 360 * (2 ** self.z) - e_tile_x) * 256
                )
            self.offset_y = math.floor(
                (
                    (2 ** self.z) / 2 - m2 * (2 ** self.z) /
                    2 / math.pi - e_tile_y
                    ) * 256
                )
            
            # Those two variables should be used to fetch image
            self.img_x, self.img_y = e_tile_x, e_tile_y
        else:
            self.img_x, self.img_y = s_tile_x, s_tile_y
            self.offset_x, self.offset_y = 0, 0

        # Those two variables should be used for coords calculation only
        self.calc_x, self.calc_y = s_tile_x, s_tile_y


def cache_tile(tile_name: str, tile_num: tuple, scale: int, tile: Image.Image):
    """Save tile in cache for faster reload of map"""

    cache_dir = os.environ.get('CACHE_DIR')

    file_name = '_'.join(str(i) for i in [tile_name, scale, *tile_num])
    file_path = cache_dir + '/' + file_name + '.png'

    tile.save(file_path)


def fetch_tile(
        tile_name: str, url: str, tile_num: tuple, scale: int
        ) -> Image.Image:
    """Get an Image object of a specific tile"""

    try:
        # Trying to get tile from cache first
        cache_dir = os.environ.get('CACHE_DIR')

        file_name = '_'.join(str(i) for i in [tile_name, scale, *tile_num])
        file_path = cache_dir + '/' + file_name + '.png'

        tile_img = Image.open(file_path)
    except FileNotFoundError:
        # Requesting encoded image from url if not found in cache
        response = requests.get(url.format(*tile_num, scale))
        decoded = io.BytesIO(response.content)  # Then decoding it

        if response.status_code == 200:  # Cuz 200 means there is a tile
            tile_img = Image.open(decoded)
            cache_tile(tile_name, tile_num, scale, tile_img)
        else:  # And everything else than 200 means there is no tile
            tile_img = get_pilimage('icon_error-404.png')
    
    return tile_img