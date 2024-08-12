from ultralytics import YOLO
import cv2 as cv
import pyautogui
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time
from datetime import datetime

with open('class.json', 'r', encoding='utf-8') as file:
    letter_dic = json.load(file)

model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
# vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
vdo = cv.VideoCapture('vdo_from_park/GS.mp4')

check = True
count = 0
skip_frames = 7
frame_counter = 0

ret, pic = vdo.read()
wordfull = ""
car_id = []
cross_car =[]
id_cross = set()
dataword = []
plateName =''
datacar_in_park = []
fps_start_time = time.time()
fps_frame_count = 0

timeNow = datetime.now().strftime("%H:%M %d-%m-%Y")
print(timeNow)

try:
    with open('line.json', 'r') as f:
        line = json.load(f)
except FileNotFoundError:
    line = []

cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

def mouse_click(event, x, y, flags, param):
    global check, line
    if event == cv.EVENT_LBUTTONDOWN:
        line.append([x, y])
        cv.putText(pic2, f'{x} {y}', (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if len(line) == 2:
            cv.line(pic2, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)
            with open('line.json', 'w') as f:
                json.dump(line, f)
    if event == cv.EVENT_RBUTTONDOWN:
        check = False

def letterCheck(id):
    global dataword,plateName,car_id,id_cross,datacar_in_park
    word = {}
    max = 0
    indexmax = 0
    for x in range(len(dataword)):
        if len(dataword[x]) >= max:
            max = len(dataword[x])
            indexmax = x
    for x in range(len(dataword[indexmax])):
        word[x] = {"x" : dataword[indexmax][x][2],
                   "word" : [[dataword[indexmax][x][0],1]]}
    
    print("===============================================")
    print(word)
    print("===============================================")
    for x in dataword:
        if x[0][1] == id:
            for y in x:
                for z in range(max):
                    if y[2] > (word[z]["x"] - (word[z]["x"]*0.1)) and y[2] < (word[z]["x"] + (word[z]["x"]*0.1)):
                        o = True
                        for k in range(len(word[z]['word'])):
                            if word[z]['word'][k][0] == y[0]:
                                word[z]['word'][k][1] += 1
                                o = False
                                break
                        if o:
                            word[z]['word'].append([y[0],1])
    finalword = ""
    for z in range(max): 
        maxd = 0
        inmax = 0
        for k in range(len(word[z]['word'])):
            if word[z]['word'][k][1] > maxd:
                maxd = word[z]['word'][k][1]
                inmax = k
        finalword += word[z]['word'][inmax][0]
    print(finalword)                         
            
                
                


    
    

if len(line) < 2:
    pic2 = pic.copy()
    while check:
        x, y = pyautogui.position()
        cv.imshow("Full Scene", pic2)
        cv.setMouseCallback('Full Scene', mouse_click)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break

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
                        for x in range(len(all_word)):
                            for y in range(len(all_word)):
                                if all_word[x][2] < all_word[y][2]:
                                    temp = all_word[y]
                                    all_word[y] = all_word[x]
                                    all_word[x] = temp
                        print(all_word)
                        dataword.append(all_word.copy())

                    if ppix[0] + pix[0] <= line[0][0] and ppix[2] + pix[0] <= line[0][0]:
                        cv.putText(pic, "cross", (904, 1002), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        letterCheck(id)

        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print(f'Error: {e}')

print('sdfsdfsdf ')
print(cross_car)
print('len cross_car '+str(len(cross_car)))
print(id_cross)

with open ('data.txt','w',encoding='utf-8')as file:
    file.write(str(dataword))
vdo.release()
cv.destroyAllWindows()


