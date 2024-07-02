from PIL import Image, ImageTk
import pytesseract as tess
import torch
import numpy as np
import cv2
import re
import matplotlib.pyplot as plt
import tkinter as tk

tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp11/weights/best.pt')
wait_count = 0

def bytes_to_cv2_image(image_bytes):
    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    return image


def get_result_index(result):
    results_arr = result.pandas().xyxy[0]
    count = len(results_arr)

    if count == 0:
        return None
    
    for i in range(count):
        if results_arr['name'][i] == 'speedlimit':
            return i

    return None


def crop_image(image, x1, y1, x2, y2):
    return image[int(y1):int(y2), int(x1):int(x2)]


def get_speed_limit(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    speed_limit = tess.image_to_string(gray_image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

    return speed_limit


def image_to_speed(image_bytes):
    global model, wait_count

    image = bytes_to_cv2_image(image_bytes)
    image = cv2.rotate(image, cv2.ROTATE_180)

    b,g,r = cv2.split(image)
    img = cv2.merge((r,g,b))

    root = tk.Tk()
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im) 
    tk.Label(root, image=imgtk).pack() 

    root.mainloop()

    result = model(image)
    idx = get_result_index(result)

    if idx is None:
        print("No speed limit sign detected!")
        return None

    xmin = result.pandas().xyxy[0]['xmin'][idx]
    ymin = result.pandas().xyxy[0]['ymin'][idx]
    xmax = result.pandas().xyxy[0]['xmax'][idx] 
    ymax = result.pandas().xyxy[0]['ymax'][idx]

    width = xmax - xmin
    height = ymax - ymin
    padding = 0.3

    xdelta = (width * padding) / 2.0
    ydelta = (height * padding) / 2.0

    xmin = xmin + xdelta
    xmax = xmax - xdelta
    ymin = ymin + ydelta
    ymax = ymax - ydelta
    
    image = crop_image(image, xmin, ymin, xmax, ymax)
    speed_limit = get_speed_limit(image)

    if speed_limit == '' or speed_limit[0] == '0':
        print("No speed limit sign detected!")
        return None
    
    print(f"Speed Limit Found: {speed_limit} km/h")
    
    return speed_limit