from eft_items import EFT_Items
from screen_capture import WindowCapture
from overlay import Overlay

import pyautogui
import pytesseract
import cv2
import tkinter as tk
import numpy as np

ITEM_SLOT_PIXEL_SIZE = 80 # all values w.r.t 3440x1440
CAPTCHA_WINDOW_X = 1490
CAPTCHA_WINDOW_WIDTH = 460
CAPTCHA_TITLE_HEIGHT = 50
CAPTCHA_ITEM_HEIGHT = 32
CAPTCHA_ITEM_CERTAINTY = 0.65
ITEM_SLOT_FHD = 64
ITEM_SIZE_MULTIPLIER = 1.25
ITEM_SLOT = ITEM_SLOT_FHD * ITEM_SIZE_MULTIPLIER

UPDATE_PERIOD_IN_MENU_IN_MS = 100
UPDATE_PERIOD_IN_RAID_IN_MS = 10*1000
update_period_in_ms = UPDATE_PERIOD_IN_MENU_IN_MS
captcha_was_active = False
menu_was_active = False


WINDOW_NAME = 'EscapeFromTarkov'
# WINDOW_NAME = 'screenshots'
screenshot_taker = WindowCapture(WINDOW_NAME)

# create the tkinter overlay
overlay = Overlay(screenshot_taker.WINDOW_TOPLEFT, screenshot_taker.WINDOW_SIZE
                    , update_period_in_ms=update_period_in_ms)

# load reference images to find windows
captcha_title_image = cv2.imread("./screenshots/captcha_title.png")
captcha_title_image = cv2.cvtColor(captcha_title_image, cv2.COLOR_BGR2RGB)
tarkov_menu_image = cv2.imread("./screenshots/tarkov_menu.png")
tarkov_menu_image = cv2.cvtColor(tarkov_menu_image, cv2.COLOR_BGR2RGB)

# load tarkov item information and icons
eft_items_grid_icons_directory = './grid_icons/'
eft_items = EFT_Items(eft_items_grid_icons_directory)

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

def check_for_template(screenshot, template):
    points = template_matching(screenshot, template, threshold=0.8)
    points = non_maximum_suppression_points(points, ITEM_SLOT_PIXEL_SIZE)

    if len(points) == 0:
        return False, None
    if len(points) > 1:
        print(f"WARNING: there is multiple locations for the given template!\n"
              f"         {points=}\n"
              f"         Using the first point.")
    return True, points[0]

def update():
    global captcha_was_active, menu_was_active, update_period_in_ms

    # locate captcha window and item name
    screenshot = screenshot_taker.take_screenshot()

    # check if in main menu
    menu_is_active, point = check_for_template(screenshot, tarkov_menu_image)
    if menu_was_active != menu_is_active:
        if menu_is_active:
            print(f"We are in the main menu. Updating every {UPDATE_PERIOD_IN_MENU_IN_MS}ms")
            update_period_in_ms = UPDATE_PERIOD_IN_MENU_IN_MS
        else:
            print(f"We are in a raid. Updating every {UPDATE_PERIOD_IN_RAID_IN_MS}ms")
            update_period_in_ms = UPDATE_PERIOD_IN_RAID_IN_MS
        menu_was_active = menu_is_active
        overlay.UPDATE_PERIOD_IN_MS = update_period_in_ms

    # check if captcha is active
    captcha_is_active, point = check_for_template(screenshot, captcha_title_image)
    if captcha_was_active and not captcha_is_active:
        overlay.remove_rectangles()

    captcha_was_active = captcha_is_active
    if not captcha_is_active:
        return
    

    # find captcha item
    captcha_item_y = point[1]+CAPTCHA_TITLE_HEIGHT
    captcha_item_image = screenshot[captcha_item_y:captcha_item_y+CAPTCHA_ITEM_HEIGHT
                                    , CAPTCHA_WINDOW_X:CAPTCHA_WINDOW_X+CAPTCHA_WINDOW_WIDTH]
    captcha_item_name = pytesseract.image_to_string(captcha_item_image)[:-1] # remove trailing '\n'
    
    captcha_item = None
    while len(captcha_item_name) > 3:
        captcha_item = eft_items.get('name', captcha_item_name, exact_match=False, verbose=False)
        if captcha_item is not None:
            break
        captcha_item_name = captcha_item_name[:-1]
    if len(captcha_item_name) <= 3:
        return
    print(f"Captcha item name: {captcha_item_name}, length={len(captcha_item_name)}")

    captcha_item_image = eft_items.get_image_from_item_name(captcha_item_name, exact_match=False)
    captcha_item_image = captcha_item_image[15:,] # remove top item label 

    # find captcha item locations on screenshot
    # TODO: x component offset bc width of window is too big
    item_locations = template_matching(screenshot, captcha_item_image, threshold=CAPTCHA_ITEM_CERTAINTY)
    item_locations = non_maximum_suppression_points(item_locations, ITEM_SLOT)
    ITEM_SIZE = (int(ITEM_SLOT*captcha_item['width']), int(ITEM_SLOT*captcha_item['height']))
    overlay.remove_rectangles()
    for point in item_locations:
        overlay.draw_rectangle(point, ITEM_SIZE)

    
def main():
    root = overlay.create_overlay()
    overlay.start_update(update)

    # start the tkinter loop
    root.mainloop()

if __name__ == '__main__':
    main()