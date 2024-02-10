import pyautogui
import pygetwindow

import numpy as np

class ScreenCapture:

    def __init__(self):
        pass

    def take_screenshot(self):
        pass

class WindowCapture(ScreenCapture):

    def __init__(self, window_title):
        self.WINDOW_TITLE = window_title

        windows = pygetwindow.getWindowsWithTitle(self.WINDOW_TITLE)
        assert len(windows) > 0, f"There is no window matching the given title({self.WINDOW_TITLE})"
        if len(windows) > 1:
            print(f"WARNING: There is {len(windows)} windows matching the given title({self.WINDOW_TITLE}).\n"
                  f"         {windows=}\n"
                  f"         The first window is selected.")

        self.WINDOW = windows[0]
        self.WINDOW_TOPLEFT = self.WINDOW.topleft
        self.WINDOW_SIZE = self.WINDOW.size

        assert self.WINDOW_SIZE[0] > 0 and self.WINDOW_SIZE[1] > 0, f"Window size must be greater than (0,0): is {self.WINDOW_SIZE}"

    def take_screenshot(self):
        screenshot = pyautogui.screenshot(region=(self.WINDOW_TOPLEFT[0],self.WINDOW_TOPLEFT[1]
                                              , self.WINDOW_SIZE[0], self.WINDOW_SIZE[1]))
        screenshot = np.array(screenshot)
        return screenshot
