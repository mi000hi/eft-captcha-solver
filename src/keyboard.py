import pyautogui
import random
import time

class Keyboard:

    def __init__(self):
        self.DELAY_KEYSTROKE_MIN_IN_MS = 5
        self.DELAY_KEYSTROKE_MAX_IN_MS = 50
        
    def alt_enter(self):
        time.sleep(random.randint(self.DELAY_KEYSTROKE_MIN_IN_MS, self.DELAY_KEYSTROKE_MAX_IN_MS)/1000.0)
        pyautogui.keyDown('alt')
        time.sleep(random.randint(self.DELAY_KEYSTROKE_MIN_IN_MS, self.DELAY_KEYSTROKE_MAX_IN_MS)/1000.0)
        pyautogui.keyDown('enter')
        time.sleep(random.randint(self.DELAY_KEYSTROKE_MIN_IN_MS, self.DELAY_KEYSTROKE_MAX_IN_MS)/1000.0)
        pyautogui.keyUp('enter')
        time.sleep(random.randint(self.DELAY_KEYSTROKE_MIN_IN_MS, self.DELAY_KEYSTROKE_MAX_IN_MS)/1000.0)
        pyautogui.keyUp('alt')