from eft_items import EFT_Items
from screen_capture import WindowCapture
from overlay import Overlay

import pyautogui
import pytesseract
import cv2
import tkinter as tk
import numpy as np

def distance(pt1, pt2):
    return np.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)

def non_maximum_suppression_points(points, distance_threshold):
    filtered_points = []
    for point in points:
        if not filtered_points:
            filtered_points.append(point)
            continue
        
        for f_point in filtered_points:
            if distance(f_point, point) < distance_threshold:
                break
        else:   
            filtered_points.append(point)
    return filtered_points
        

def template_matching(image, template, threshold=0.8):
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    loc = np.where( result >= threshold)
    points = zip(*loc[::-1])
    return points

def main():
    ITEM_SLOT_PIXEL_SIZE = 80 # all values w.r.t 3440x1440
    CAPTCHA_WINDOW_X = 1490
    CAPTCHA_WINDOW_WIDTH = 460
    CAPTCHA_TITLE_HEIGHT = 50
    CAPTCHA_ITEM_HEIGHT = 32
    CAPTCHA_ITEM_CERTAINTY = 0.7
    ITEM_SLOT_FHD = 64
    ITEM_SIZE_MULTIPLIER = 1.25
    ITEM_SLOT = ITEM_SLOT_FHD * ITEM_SIZE_MULTIPLIER
    

    window_name = 'EscapeFromTarkov'
    # window_name = 'Windows-Fotoanzeige'
    screenshot_taker = WindowCapture(window_name)

    # create the tkinter overlay
    overlay = Overlay(screenshot_taker.WINDOW_TOPLEFT, screenshot_taker.WINDOW_SIZE)
    root = overlay.create_overlay()

    # load reference image to find captcha
    captcha_title_image = cv2.imread("./screenshots/captcha_title.png")
    captcha_title_image = cv2.cvtColor(captcha_title_image, cv2.COLOR_BGR2RGB)

    # load tarkov item information and icons
    eft_items_grid_icons_directory = './grid_icons/'
    eft_items = EFT_Items(eft_items_grid_icons_directory)

    # locate captcha window and item name
    screenshot = screenshot_taker.take_screenshot()
    points = template_matching(screenshot, captcha_title_image, threshold=0.8)
    points = non_maximum_suppression_points(points, ITEM_SLOT_PIXEL_SIZE)
    # TODO: assert point found
    if len(points) > 1:
        print(f"WARNING: there is multiple locations for the captcha window!\n"
              f"         {points=}\n"
              f"         Using the first point.")
    point = points[0]

    captcha_item_y = point[1]+CAPTCHA_TITLE_HEIGHT
    captcha_item_image = screenshot[captcha_item_y:captcha_item_y+CAPTCHA_ITEM_HEIGHT
                                    , CAPTCHA_WINDOW_X:CAPTCHA_WINDOW_X+CAPTCHA_WINDOW_WIDTH]
    captcha_item_name = pytesseract.image_to_string(captcha_item_image)[:-1] # remove trailing '\n'
    print(f"Captcha item name: {captcha_item_name}")

    captcha_item = eft_items.get('name', captcha_item_name)
    captcha_item_image = eft_items.get_image_from_item_name(captcha_item_name)
    captcha_item_image = captcha_item_image[15:,] # remove top item label 

    # find captcha item locations
    # TODO: x component offset bc width of window is too big
    item_locations = template_matching(screenshot, captcha_item_image, threshold=CAPTCHA_ITEM_CERTAINTY)
    item_locations = non_maximum_suppression_points(item_locations, ITEM_SLOT_PIXEL_SIZE)
    ITEM_SIZE = (int(ITEM_SLOT*captcha_item['width']), int(ITEM_SLOT*captcha_item['height']))
    for point in item_locations:
        overlay.draw_rectangle(point, ITEM_SIZE)

    # start the tkinter loop
    root.mainloop()

if __name__ == '__main__':
    main()