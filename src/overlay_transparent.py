import tkinter as tk

class OverlayTransparent:

    def __init__(self, overlay_position:tuple, overlay_size:tuple, transparent_color:str="#fffffe"
                 , border_thickness:int=3, update_period_in_ms:int=1000):
        self.POSITION = overlay_position
        self.SIZE = overlay_size
        self.WIDTH, self.HEIGHT = overlay_size

        self.TRANSPARENT_COLOR = transparent_color
        self.BORDER_THICKNESS = border_thickness

        self.UPDATE_PERIOD_IN_MS = update_period_in_ms

        self.rectangles = []

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
    
    def draw_rectangle(self, topleft:tuple, size:tuple, thickness:int=2, color:tuple="#ffffff"):
        rectangle = tk.Frame(self.root, width=size[0], height=size[1], bg=color)
        rectangle.place(x=topleft[0], y=topleft[1])
        self.rectangles.append(rectangle)
        rectangle = tk.Frame(self.root, width=size[0]-2*thickness, height=size[1]-2*thickness, bg=self.TRANSPARENT_COLOR)
        rectangle.place(x=topleft[0]+thickness, y=topleft[1]+thickness)
        self.rectangles.append(rectangle)

    def remove_rectangles(self):
        for rectangle in self.rectangles:
            rectangle.destroy()
        self.rectangles = []

    def start_update(self, function):
        function()
        self.root.after(self.UPDATE_PERIOD_IN_MS, self.start_update, function)