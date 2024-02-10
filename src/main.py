from api import EFT_Items
from Screen_Capture import WindowCapture
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

def draw_rect(root, x,y,w,h, thickness=2):
    f = tk.Frame(root, width=w, height=h, bg='green')
    f.place(x=x, y = y)
    f = tk.Frame(root, width=w-2*thickness, height=h-2*thickness, bg="#fffffe")
    f.place(x=x+thickness, y=y+thickness)

def main():
    ITEM_PIXEL_SIZE = 80

    eft_items_grid_icons_directory = '../grid_icons/'
    eft_items = EFT_Items(eft_items_grid_icons_directory)

    window_name = 'EscapeFromTarkov'
    screenshot_taker = WindowCapture(window_name)
    screenshot = screenshot_taker.take_screenshot()

    # search captcha window
    image = cv2.imread("./screenshots/captcha_title.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    captcha_title_image = image.copy()
    points = template_matching(screenshot, captcha_title_image, threshold=0.8)
    points = non_maximum_suppression_points(points, 80)
    point = points[0]

    x = 1490
    y = point[1]+50
    w = 460
    h = 32
    captcha_item_image = screenshot[y:y+h, x:x+w]
    captcha_item_text = pytesseract.image_to_string(captcha_item_image)[:-1]
    print(captcha_item_text)


    captcha_item_name = captcha_item_text
    captcha_item_image = eft_items.get_image_from_item_name(captcha_item_name)
    captcha_item_image = captcha_item_image[15:,]

    cv2.imshow("image", captcha_item_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # template matching
    # TODO: x component offset bc width of window is too big
    points = template_matching(screenshot, captcha_item_image, threshold=0.6)
    points = non_maximum_suppression_points(points, ITEM_PIXEL_SIZE)

    # show points as tkinter overlay
    overlay = Overlay(screenshot_taker.WINDOW_TOPLEFT, screenshot_taker.WINDOW_SIZE)
    root = overlay.create_overlay()

    # drawing rectangle
    draw_rect(root, point[0], point[1], 460, 50)
    draw_rect(root, x, y, w, h)

    for point in points:
        draw_rect(root, point[0], point[1], 80, 80)

    root.mainloop()

if __name__ == '__main__':
    main()