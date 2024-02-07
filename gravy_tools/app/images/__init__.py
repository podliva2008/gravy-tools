from PIL import Image, ImageTk

import os

def get_imagetk(image_name: str) -> ImageTk.PhotoImage:
    """Gets image from /images and returns as tkinter PhotoImage object"""

    image_path = os.path.dirname(os.path.realpath(__file__)) + '/' + image_name
    original_image = Image.open(image_path)
    return ImageTk.PhotoImage(original_image)

def get_pilimage(image_name: str) -> Image.Image:
    """Gets image from /images and returns as PIL Image object"""

    image_path = os.path.dirname(os.path.realpath(__file__)) + '/' + image_name
    return Image.open(image_path)