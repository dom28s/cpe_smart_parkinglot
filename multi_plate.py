from ultralytics import YOLO
import cv2 as cv
import json
import numpy as np
import time
from datetime import datetime
import os
from PIL import Image
from shapely.geometry import Polygon
import multi_variable
import mysql.connector
import difflib



def plateProgram():
    conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="projects"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM car")
    car_row = cursor.fetchall()

    cursor.execute("SELECT * FROM `camera`")
    camara_row = cursor.fetchall()

    with open('class.json', 'r', encoding='utf-8') as file:
        letter_dic = json.load(file)

    model = YOLO('model/yolov8n.pt')
    modelP = YOLO('model/licen_100b.pt')
    modelC = YOLO('model/thaiChar_100b.pt')
    vdo = cv.VideoCapture('vdo_from_park/GF.mp4')
    # vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

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
    line2first =[]


    no_regisID=[]

    try:
        with open('line.json', 'r') as f:
            allline = json.load(f)
    except FileNotFoundError:
        allline = []


    def letterCheck(id, timeNow, pic_black):
        # Ensure all required variables are initialized
        dataword, plateName, car_id, id_cross, datacar_in_park
        word = {}
        max = 0
        indexmax = 0
        finalword = ""  # Initialize finalword here

        # Processing dataword
        for x in range(len(dataword)):
            if len(dataword[x]) >= max and dataword[x][0][1] == id:
                max = len(dataword[x])
                indexmax = x
        
        for x in range(len(dataword[indexmax])):
            word[x] = {"x": dataword[indexmax][x][2], "word": [[dataword[indexmax][x][0], 1]]}

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
                                word[z]['word'].append([y[0], 1])

        # Construct finalword
        for z in range(max):
            maxd = 0
            inmax = 0
            for k in range(len(word[z]['word'])):
                if word[z]['word'][k][1] > maxd:
                    maxd = word[z]['word'][k][1]
                    inmax = k
            finalword += word[z]['word'][inmax][0]
        
        print(finalword)

        max_per = 0
        best_word = None

        # Comparing finalword to database entries
        for db in car_row:
            matcher = difflib.SequenceMatcher(None, db[3], finalword)
            per = matcher.ratio() * 100

            if per > max_per:
                max_per = per
                best_word = db[3]

        print(f'{max_per} {best_word}')
        multi_variable.finalword = finalword
        print(finalword)
        print('++++++++++')

        # Decision making based on match percentage
        if max_per >= 75 and id not in no_regisID:
            finalword = best_word

        if max_per < 75 and id not in no_regisID:
            no_regisID.append(id)
            if not os.path.exists('no_regis'):
                with open('no_regis', 'w', encoding='utf-8') as file:
                    file.write(f'{finalword} {timeNow}\n')
            else:
                with open('no_regis', 'a', encoding='utf-8') as file:
                    file.write(f'{finalword} {timeNow}\n')

            # Track cars that have crossed
        if id not in car_hascross:
            car_hascross.append(id)
            cross_car.append([finalword, timeNow])
            print('----=------=------=----')
            print(cross_car)
            if not os.path.exists('plateSave'):
                with open('plateSave', 'w', encoding='utf-8') as file:
                    for x in range(len(cross_car)):
                        file.write(f'{cross_car[x][0]} {timeNow}\n')
            else:
                with open('plateSave', 'a', encoding='utf-8') as file:
                    file.write(f'{finalword} {timeNow}\n')
            print('----=------=------=----')

            # Save the plate image
            current_time = datetime.now()
            day = current_time.strftime('%d-%m-%Y')
            hour = current_time.strftime('%H%M')
            sec = current_time.strftime('%S')

            save_dir = f'plateCross/{day}/{hour}/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            filename = f'{finalword}_{hour}_{sec}.jpg'
            ret, pic_save = vdo.read()
            cv.imwrite(f'{save_dir}{filename}', pic_save)

            

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


    def apply_otsu_threshold(image):
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)
        _, binary_image = cv.threshold(blurred_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        return binary_image


    def bbox_to_polygon(pix):
        return Polygon([
            (pix[0], pix[1]),  # มุมบนซ้าย
            (pix[2], pix[1]),  # มุมบนขวา
            (pix[2], pix[3]),  # มุมล่างขวา
            (pix[0], pix[3])   # มุมล่างซ้าย
        ])


    def create_left_polygon(line2_points, img_width, img_height):
        p1, p2 = line2_points
        return Polygon([
            (0, 0),             # มุมบนซ้ายของภาพ
            (p1[0], p1[1]),     # จุดแรกของ line2
            (p2[0], p2[1]),     # จุดที่สองของ line2
            (0, img_height)     # มุมล่างซ้ายของภาพ
        ])


    def is_intersecting(car_polygon, left_polygon):
        if car_polygon.intersects(left_polygon):
            intersection_area = car_polygon.intersection(left_polygon).area
            car_area = car_polygon.area
            
            if (intersection_area / car_area) > 0.001:
                return True
        return False


    while True:
        try:
            ret, pic = vdo.read()
            width = vdo.get(cv.CAP_PROP_FRAME_WIDTH)
            height = vdo.get(cv.CAP_PROP_FRAME_HEIGHT)
            timeNow = datetime.now().strftime("%H:%M | %d/%m/%Y")


            if not ret:
                print("อ่านเฟรมไม่สำเร็จ กำลังพยายามใหม่...")
                break
            
            # skip frame
            frame_counter += 1
            if frame_counter % (skip_frames + 1) != 0:
                continue

            pic_black = pic.copy()

            cv.rectangle(pic_black, (0, 0), (x_threshold, pic.shape[0]), (0, 0, 0), thickness=cv.FILLED)

            line1 = ((allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]))
            line2 = ((allline[1][0][0], allline[1][0][1]), (allline[1][1][0], allline[1][1][1]))
            
            result_model = model.track(pic_black, conf=0.5, classes=2, persist=True)

            for e in result_model[0].boxes:
                name = result_model[0].names[int(e.cls)]
                pix = e.xyxy.tolist()[0]
                id = int(e.id)
                
                car = (int(pix[0]), int(pix[1]), int(pix[2]), int(pix[3]))

                car_polygon = bbox_to_polygon(pix)
                left_polygon = create_left_polygon(line2, width, height)

                # line 2 check dont know why
                if is_intersecting(car_polygon, left_polygon):
                    line2first.append(id)
                    cv.putText(pic, f"hit 2 : {id}", (1000, 1030), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    for x in carhit:
                        if x == id:
                            letterCheck(id,timeNow,pic_black)

                            # CAR DETECTION
                crop_car = pic_black[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
                resultP = modelP(crop_car, conf=0.5)

                            # PLATE DETECTION
                for x in resultP[0].boxes:
                    pname = resultP[0].names[int(x.cls)]
                    ppix = x.xyxy.tolist()[0]

                    crop_plate = crop_car[int(ppix[1]):int(ppix[3]), int(ppix[0]):int(ppix[2])]
                    crop_plate = cv.resize(crop_plate, (320, 320))

                    # binary_image = apply_otsu_threshold(crop_plate)
                    # crop_plate = cv.merge([binary_image] * 3)

                    resultC = modelC(crop_plate, conf=0.5)

                    all_word = []
                                # LETTER DETECTION
                    for y in resultC[0].boxes:
                        cname = resultC[0].names[int(y.cls)]
                        cpix = y.xyxy.tolist()[0]
                        try:
                            if len(letter_dic[str(cname)]) ==1:
                                all_word.append([letter_dic[str(cname)], id, cpix[0]])


                        except KeyError:
                            print("Key not found in data dictionary")

                        print(letter_dic[cname])
    
                    if len(all_word) != 0:
                        for x in range(len(all_word)):
                            for y in range(len(all_word)):
                                if all_word[x][2] < all_word[y][2]:
                                    temp = all_word[y]
                                    all_word[y] = all_word[x]
                                    all_word[x] = temp
                        print(all_word)
                        dataword.append(all_word.copy())
                        
                    if is_line_intersecting_bbox(car, line1):
                        if id in line2first:
                            cv.putText(pic, f"hit 2 first : {id}", (1000, 1000), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        elif not id in carhit:
                            carhit.append(id)
                            
            print(timeNow)
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


plateProgram()