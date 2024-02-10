from api import EFT_Items
from Screen_Capture import WindowCapture

import pyautogui
import cv2
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
        

def template_matching(image, template, threshold=0.8):
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    loc = np.where( result >= threshold)
    points = zip(*loc[::-1])
    return points

def main():
    ITEM_PIXEL_SIZE = 80

    eft_items_grid_icons_directory = './grid_icons/'
    eft_items = EFT_Items(eft_items_grid_icons_directory)

    window_name = 'EscapeFromTarkov'
    screenshot_taker = WindowCapture(window_name)
    screenshot = screenshot_taker.take_screenshot()

    captcha_item_name = 'Freeman crowbar'
    captcha_item_image = eft_items.get_image_from_item_name(captcha_item_name)

    # template matching
    points = template_matching(screenshot, captcha_item_image)
    points = non_maximum_suppression_points(points, ITEM_PIXEL_SIZE)

    # show points as tkinter overlay

if __name__ == '__main__':
    main()