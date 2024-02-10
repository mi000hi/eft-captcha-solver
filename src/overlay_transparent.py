import tkinter as tk

class OverlayTransparent:

    def __init__(self, overlay_position:tuple, overlay_size:tuple, transparent_color:str="#fffffe"
                 , border_thickness:int=3):
        self.POSITION = overlay_position
        self.SIZE = overlay_size
        self.WIDTH, self.HEIGHT = overlay_size

        self.TRANSPARENT_COLOR = transparent_color
        self.BORDER_THICKNESS = border_thickness

    def create_overlay(self):
        self.root = tk.Tk()
        self.root.title("tkinter overlay")
        self.root.geometry("%dx%d+%d+%d" % (self.WIDTH,self.HEIGHT,self.POSITION[0],self.POSITION[1]))
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg='red')

        # make specified color transparent
        self.root.wm_attributes('-transparentcolor', self.TRANSPARENT_COLOR)

        # add transparent frame
        self.transparent_frame = tk.Frame(self.root, width=self.WIDTH-2*self.BORDER_THICKNESS
                                          , height=self.HEIGHT-2*self.BORDER_THICKNESS, bg=self.TRANSPARENT_COLOR)
        self.transparent_frame.place(x=self.BORDER_THICKNESS,y=self.BORDER_THICKNESS)

        return self.root