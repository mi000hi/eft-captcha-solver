from overlay_transparent import OverlayTransparent

import tkinter as tk

class Overlay(OverlayTransparent):
    
    def __init__(self, overlay_position:tuple, overlay_size:tuple, transparent_color:str="#fffffe"
                 , border_thickness:int=3):
        super().__init__(overlay_position, overlay_size, transparent_color, border_thickness)