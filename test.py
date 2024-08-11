from ultralytics import YOLO
import cv2 as cv
import pyautogui
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

with open('class.json', 'r', encoding='utf-8') as file:
    letter_dic = json.load(file)

model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')

check = True
count = 0
skip_frames = 6
frame_counter = 0

vdo = cv.VideoCapture('vdo_from_park/GF.mp4')
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

ret, pic = vdo.read()
wordfull = ""
park = []
car_id = []
cross_car =[]
plateName =''

fps_start_time = time.time()
fps_frame_count = 0

try:
    with open('line.json', 'r') as f:
        line = json.load(f)
except FileNotFoundError:
    line = []

cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

def mouse_click(event, x, y, flags, param):
    global check, line, park
    if event == cv.EVENT_LBUTTONDOWN:
        line.append([x, y])
        cv.putText(pic2, f'{x} {y}', (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if len(line) == 2:
            cv.line(pic2, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)
            with open('line.json', 'w') as f:
                json.dump(line, f)
    if event == cv.EVENT_RBUTTONDOWN:
        check = False

# def letterCheck(id):
#     global wordfull
#     max = 0
#     datamax = 0
#     print('id a '+str(id))
#     print("len dataword "+str(len(dataword)))
#     print('data word'+str(dataword))
#     print(' ')

#     for i in range(len(dataword)):
#         for i2 in range(len(dataword[i])):
#             if dataword[i][i2][1] == id:
#                 car_id.append(dataword[i][i2])

#     print('car id '+str(car_id))
#     print(' ')
#     # for x in range(len(car_id)):
#     #     for x in range
#     #     if car_id[x][2]




#     for x in range(len(car_id)):
#         if len(car_id[x]) > datamax:
#             max = x
#             datamax = len(car_id[x])
#     for x in range(len(car_id[max])):
#         for j in range(len(car_id[max])):
#             if car_id[max][x][1] < car_id[max][j][1]:
#                 t = car_id[max][x]
#                 car_id[max][x] = car_id[max][j]
#                 car_id[max][j] = t
#     for x in car_id[max]:
#         wordfull += x[0]+" "
#     print("this is "+wordfull)
#     car_id.clear()

def letterCheck(id):
    global wordfull,plateName
    car_id = []

    print('id: ' + str(id))
    print("len dataword: " + str(len(dataword)))
    print('dataword: ' + str(dataword))
    print(' ')

    # Collect items with the matching id
    for sublist in dataword:
        for item in sublist:
            if item[1] == id:
                car_id.append(item,id)

    car_id = sorted(car_id, key=lambda x: x[2])
    print(car_id)

    for i in range(len(car_id)):
        for i2 in range(len(car_id[i])):
            print(car_id[i][0])
            name = str(car_id[i][0])
            plateName = plateName+name

    print("this is " + plateName)
    cross_car.append(plateName)
    car_id.clear()
    plateName =''

    # print(cross_car)



# def plate(ppix,line,pix,id):
#     print('plate start')
#     print("len data"+str(len(dataword)))
#     for i in range(len(dataword)):
#         for i2 in range(i):
#             if dataword[i][i2][1] == id:
#                 car_id.append(dataword[i][i2])
#                 break
    # print('car id len '+str(len(car_id)))
    # print("car id "+str(car_id))
    # print(' ')
    



if len(line) < 2:
    pic2 = pic.copy()
    while check:
        x, y = pyautogui.position()
        cv.imshow("Full Scene", pic2)
        cv.setMouseCallback('Full Scene', mouse_click)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break

dataword = []

while True:
    try:
        ret, pic = vdo.read()
        if not ret:
            print("Failed to read frame. Exiting...")
            break

        fps_frame_count += 1

        if time.time() - fps_start_time >= 1.0:  # Update FPS every second
            fps = fps_frame_count
            fps_frame_count = 0
            fps_start_time = time.time()
        else:
            fps = fps_frame_count

        cv.putText(pic, f"FPS: {fps}", (5, 60), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv.putText(pic, "Press P To Exit", (5,30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        frame_counter += 1
        if frame_counter % (skip_frames + 1) != 0:
            continue

        if len(line) == 2:
            cv.line(pic, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)
        # pic = cv.resize(pic,(1280,720))
        result_model = model.track(pic, conf=0.5, classes=2, persist=True)

        for e in result_model[0].boxes:
            name = result_model[0].names[int(e.cls)]
            pix = e.xyxy.tolist()[0]
            id = int(e.id)


            if pix[0] > 500:

                        # CAR DETECTION
                cv.putText(pic, "%s  %.0f" % (str(name), float(e.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

                crop_car = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
                resultP = modelP(crop_car, conf=0.5)

                        # PLATE DETECTION
                for x in resultP[0].boxes:
                    pname = resultP[0].names[int(x.cls)]
                    ppix = x.xyxy.tolist()[0]

                    cv.rectangle(crop_car, (int(ppix[0]), int(ppix[1])), (int(ppix[2]), int(ppix[3])), (255, 0, 0), 2)

                    crop_plate = crop_car[int(ppix[1]):int(ppix[3]), int(ppix[0]):int(ppix[2])]
                    crop_plate = cv.resize(crop_plate, (320, 250))
                            # crop_plate = upscale_image(crop_plate)
                    resultC = modelC(crop_plate, conf=0.5)

                    all_word = []

                            # LETTER DETECTION
                    for y in resultC[0].boxes:
                        cname = resultC[0].names[int(y.cls)]
                        cpix = y.xyxy.tolist()[0]
                        try:
                            if len(letter_dic[str(cname)]) > 2:
                                all_word.append([letter_dic[str(cname)], id, 10000])
                            else:
                                all_word.append([letter_dic[str(cname)], id, cpix[0]])

                        except KeyError:
                            print("Key not found in data dictionary")
                        cv.putText(crop_plate, str(cname), (int(cpix[0]), int(cpix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv.rectangle(crop_plate, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)
                        print(letter_dic[cname])
                        cv.imshow('df', crop_plate)
                            
                        if len(all_word) != 0:
                            dataword.append(all_word.copy())

                        if ppix[0] + pix[0] <= line[0][0] and ppix[2] + pix[0] <= line[0][0]:
                            cv.putText(pic, "cross", (904, 1002), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            for x in range(10):
                                print('cross')
                                print('ID b '+str(id))
                            letterCheck(id)
                            
                            # plate(ppix,line,pix,id)

        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print(f'Error: {e}')

# letterCheck()
print(cross_car)
with open ('data.txt','w',encoding='utf-8')as file:
    file.write(str(dataword))
print(len(cross_car))
vdo.release()
cv.destroyAllWindows()


