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
vdo = cv.VideoCapture('vdo_from_park/GF.mp4')
# vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

check = True
check2 = True
count = 0
skip_frames = 8
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
x_threshold=800
timeNow = datetime.now().strftime("%H:%M %d-%m-%Y")

green = (0, 255, 0)  # empty
red = (0, 0, 255)    # not empty
blue = (255, 0, 0)   # unknown
yellow = (0, 255, 255)  # undefined occupancy

carhit = {
    "CarID" : [],
    "Time" : []
}
carinpark = []


try:
    with open('line.json', 'r') as f:
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
                with open('line.json', 'w') as f:
                    json.dump(allline, f)
                check = False
    if event == cv.EVENT_RBUTTONDOWN:
        check = False


# def letterCheck(id):
#     global dataword,plateName,car_id,id_cross,datacar_in_park
#     word = {}
#     max = 0
#     indexmax = 0
#     for x in range(len(dataword)):
#         if len(dataword[x]) >= max:
#             max = len(dataword[x])
#             indexmax = x
#     for x in range(len(dataword[indexmax])):
#         word[x] = {"x" : dataword[indexmax][x][2],
#                    "word" : [[dataword[indexmax][x][0],1]]}
#     print("===============================================")
#     print(word)
#     print("===============================================")
#     for x in dataword:
#         if x[0][1] == id:
#             for y in x:
#                 for z in range(max):
#                     if y[2] > (word[z]["x"] - (word[z]["x"]*0.1)) and y[2] < (word[z]["x"] + (word[z]["x"]*0.1)):
#                         o = True
#                         for k in range(len(word[z]['word'])):
#                             if word[z]['word'][k][0] == y[0]:
#                                 word[z]['word'][k][1] += 1
#                                 o = False
#                                 break
#                         if o:
#                             word[z]['word'].append([y[0],1])
#     finalword = ""
#     for z in range(max): 
#         maxd = 0
#         inmax = 0
#         for k in range(len(word[z]['word'])):
#             if word[z]['word'][k][1] > maxd:
#                 maxd = word[z]['word'][k][1]
#                 inmax = k
#         finalword += word[z]['word'][inmax][0]
#     print(finalword)
#     cross_car.append([finalword,timeNow]) 


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
    for x in range(len(crop_car)):
        if id in cross_car[x][0]:
            print('al add')
        else:
            cross_car.append([id,finalword,timeNow]) 



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
                        

def check():
    global carhit
    print(carhit)




ret, pic = vdo.read()
pic2 = pic.copy()

if len(allline) < 2 :
    while check:
        cv.imshow("Full Scene", pic2)
        cv.setMouseCallback('Full Scene', mouse_click)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break


carhit_test =[]
carhit_test2=[]

while True:
    try:
        ret, pic = vdo.read()
        if not ret:
            print("Failed to read frame. Exiting...")
            break
        
        # skip frame
        frame_counter += 1
        if frame_counter % (skip_frames + 1) != 0:
            continue

        pic_black = pic.copy()
        
        
        cv.rectangle(pic_black, (0, 0), (x_threshold, pic.shape[0]), (0, 0, 0), thickness=cv.FILLED)
        cv.putText(pic, "Press P To Exit", (5,30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(pic, "Press H To Exit", (5,60), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(pic, "Press X To Stop", (5,120), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        line1 = ((allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]))
        line2 = ((allline[1][0][0], allline[1][0][1]), (allline[1][1][0], allline[1][1][1]))

        cv.line(pic, (allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]), yellow, 5)
        cv.line(pic, (allline[1][0][0], allline[1][0][1]), (allline[1][1][0], allline[1][1][1]), blue, 5)

        result_model = model.track(pic_black, conf=0.5, classes=2, persist=True)

        for e in result_model[0].boxes:
            name = result_model[0].names[int(e.cls)]
            pix = e.xyxy.tolist()[0]
            id = int(e.id)

            car = (int(pix[0]), int(pix[1]), int(pix[2]), int(pix[3]))

                        # CAR DETECTION
            cv.putText(pic, "%s  %.0f" % (str(name), float(e.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

            crop_car = pic_black[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
            resultP = modelP(crop_car, conf=0.5)

                        # PLATE DETECTION
            for x in resultP[0].boxes:
                pname = resultP[0].names[int(x.cls)]
                ppix = x.xyxy.tolist()[0]
                cv.rectangle(crop_car, (int(ppix[0]), int(ppix[1])), (int(ppix[2]), int(ppix[3])), (255, 0, 0), 2)

                crop_plate = crop_car[int(ppix[1]):int(ppix[3]), int(ppix[0]):int(ppix[2])]
                crop_plate = cv.resize(crop_plate, (320, 250))

                # gray_image = cv.cvtColor(crop_plate, cv.COLOR_BGR2GRAY)
                # blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
                # _, binary_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
                # binary_image_3channel = cv.merge([binary_image, binary_image, binary_image])

                # resultC = modelC(binary_image_3channel, conf=0.5)

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

                    # cv.putText(binary_image_3channel, str(cname), (int(cpix[0]), int(cpix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # cv.rectangle(binary_image_3channel, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)
                    
                    cv.putText(crop_plate, str(cname), (int(cpix[0]), int(cpix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv.rectangle(crop_plate, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)

                    print(letter_dic[cname])

                    # cv.imshow('df', binary_image_3channel)
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


                # if is_line_intersecting_bbox(car, line1):
                #     if not id in carhit['CarID']:
                #         carhit['CarID'].append(id)
                #         carhit['Time'].append(time.time())
                #     else:
                #         carhit['Time'][carhit['CarID'].index(id)] = time.time()
                #     print(carhit)
                #     cv.putText(pic, "hit 1", (1000, 1000), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # if is_line_intersecting_bbox(car, line2):
                #     if id in carhit['CarID']:
                #         carinpark.append(id)
                #         carhit['Time'].pop(carhit['CarID'].index(id))
                #         carhit['CarID'].remove(id)
                        # cv.putText(pic, "hit 2", (1000, 1030), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                if is_line_intersecting_bbox(car, line1):
                    if not id in carhit_test:
                        carhit_test.append(id)
                if is_line_intersecting_bbox(car, line1):
                    for x in carhit_test:
                        if x == id:
                            letterCheck(id)
                            
                    
                    

        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break

    except Exception as e:
        print(f'Error: {e}')

print('_______ ')
print(cross_car)
print('_______ ')
# print('len cross_car '+str(len(cross_car)))
print('car hit test '+str(carhit_test))
print(carinpark)

with open ('data.txt','w',encoding='utf-8')as file:
    file.write(str(dataword))
vdo.release()
cv.destroyAllWindows()
