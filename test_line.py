from ultralytics import YOLO
import cv2 as cv
import json
import numpy as np
import time
from datetime import datetime
import os
from PIL import Image


with open('class.json', 'r', encoding='utf-8') as file:
    letter_dic = json.load(file)

model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
# vdo = cv.VideoCapture('vdo_from_park/GF.mp4')
# vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
vdo = cv.VideoCapture(0)

cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

check = True
check2 = True
count = 0
skip_frames = 7
frame_counter = 0

wordfull = ""
car_id = []
cross_car =[]
id_cross = set()
dataword = []
plateName =''
datacar_in_park = []
fps_start_time = time.time()
fps_frame_count = 0
line = []
x_threshold=710

green = (0, 255, 0)  # empty
red = (0, 0, 255)    # not empty
blue = (255, 0, 0)   # unknown
yellow = (0, 255, 255)  # undefined occupancy

carhit = []
carinpark = []
car_hascross=[]


try:
    with open('line_test2.json', 'r') as f:
        allline = json.load(f)
except FileNotFoundError:
    allline = []


def mouse_click(event, x, y, flags, param):
    global check, line
    if event == cv.EVENT_LBUTTONDOWN:
        line.append([x, y])
        cv.putText(pic2, f'{x} {y}', (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if len(line) == 2:
            cv.line(pic2, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)
            allline.append(line.copy())
            line.clear()

            if (len(allline)) ==2:
                with open('line_test2.json', 'w') as f:
                    json.dump(allline, f)
                check = False
    if event == cv.EVENT_RBUTTONDOWN:
        check = False


def is_line_intersecting_bbox(car, line):
    x1, y1, x2, y2 = car
    (x3, y3), (x4, y4) = line
    edges = [
        ((x1, y1), (x2, y1)),  # Top
        ((x2, y1), (x2, y2)),  # Right
        ((x2, y2), (x1, y2)),  # Bottom
        ((x1, y2), (x1, y1))   # Left
    ]

    for edge in edges:
        if do_intersect(edge, line):
            return True
    return False


def do_intersect(line1, line2):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    (A, B), (C, D) = line1, line2
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


carhit = []  # เก็บรถที่ชนเส้น line1

ret, pic = vdo.read()
pic2 = pic.copy()

if len(allline) < 2 :
    while check:
        width = vdo.get(cv.CAP_PROP_FRAME_WIDTH)
        height = vdo.get(cv.CAP_PROP_FRAME_HEIGHT)
        cv.line(pic2,(x_threshold,0),(x_threshold,int(height)),red,2)
        cv.imshow("Full Scene", pic2)
        cv.setMouseCallback('Full Scene', mouse_click)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break

while True:
    try:
        ret, pic = vdo.read()
        width = vdo.get(cv.CAP_PROP_FRAME_WIDTH)
        height = vdo.get(cv.CAP_PROP_FRAME_HEIGHT)



        pic = cv.flip(pic,1)
        
        # skip frame
        frame_counter += 1
        if frame_counter % (skip_frames + 1) != 0:
            continue

        # Define the lines
        line1 = ((allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]))    # yellow
        line2 = ((allline[1][0][0], allline[1][0][1]), (allline[1][1][0], allline[1][1][1]))    # blue

        # Draw the lines on the frame
        cv.line(pic, (allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]), yellow, 2)
        cv.line(pic, (allline[1][0][0], allline[1][0][1]), (allline[1][1][0], allline[1][1][1]), blue, 2)
        
        # Run YOLO model
        result_model = model.track(pic, conf=0.5, classes=0, persist=True)

        for e in result_model[0].boxes:
            name = result_model[0].names[int(e.cls)]
            pix = e.xyxy.tolist()[0]
            id = int(e.id)
            
            car = (int(pix[0]), int(pix[1]), int(pix[2]), int(pix[3]))

            # Display the bounding box and object info
            cv.putText(pic, "%s  %.0f" % (str(name), float(e.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

            cv.putText(pic,str(carhit),(300,50),cv.FONT_HERSHEY_SIMPLEX, 1,red,2)

            # Check intersection with line1 (yellow)
            # Check intersection with line1 (yellow)
            if is_line_intersecting_bbox(car, line1):
                print(f"Checking intersection for Car {id} with line1")  # Debugging statement

                if id not in carhit:
                    carhit.append(id)
                    print(f"Car {id} hit line1 and added to carhit")  
                    cv.putText(pic, f"hit 1 : {id}", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    # Print if it's not added because it's already in carhit
                    cv.putText(pic, f"hit 1 : {id}", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)




            # Check intersection with line2 (blue)
            if is_line_intersecting_bbox(car, line2):
                print(f"Car {id} hit line2")  # Debugging statement
                cv.putText(pic, f"hit 2 : {id}", (50, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                for x in carhit:
                    cv.putText(pic, f"{id} hit all", (50, 150), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    if x == id:
                        timeNow = datetime.now().strftime("%H:%M | %d/%m/%Y")
                        print(f"Car {id} has crossed both lines at {timeNow}")  # Debugging statement
                     
        cv.imshow('Full Scene', pic)

        if cv.waitKey(1) & 0xFF == ord('p'):
            break

    except Exception as e:
        print(f'Error: {e}')


print('_______ ')
print(cross_car)
print(f'id that has cross : {car_hascross}')
print('_______ ')


vdo.release()
cv.destroyAllWindows()


