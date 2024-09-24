import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from ultralytics import YOLO
import time
from datetime import datetime
import mysql.connector
from PIL import ImageFont, ImageDraw, Image
import difflib
import threading
import multi_plate_test
import multi_top_test
import multi_variable





def topProgram(model):
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="projects"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `parkingspace`")
    cam2 = cursor.fetchall()
    plate_cross =[]
    with open('class.json', 'r', encoding='utf-8') as file:
        letter_dic = json.load(file)
        

    vdo = cv.VideoCapture('vdo_from_park/topCam.mp4')

    frame_counter = 0
    skip_frames = 15
    check = True


    cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    # Define colors for display
    green = (0, 255, 0)  # Available
    red = (0, 0, 255)    # Occupied
    yellow = (0, 255, 255)  # Obstacle
    blue = (255,0,0) #บุคคลภายนอก
    purple = (128, 0, 128)

    points = []  
  
    park_data = []
    park_id = 0  

    enter_data = []
   
    check = True  

    ajan ={}

    def load_park_from_json(filename):
        global park_data, enter_data
        if os.path.exists(filename):
            if filename == 'park.json':
                with open(filename, 'r') as f:
                    park_data = json.load(f)
                return park_data

            if filename == 'enter.json':
                with open(filename, 'r') as f:
                    enter_data = json.load(f)
                    print(f'Loaded enter_data: {enter_data}') 
                    return enter_data



    def polygon_area(polygon):
        """ Calculate the area of a polygon """
        return Polygon(polygon).area

    def polygon_intersection_area(polygon1, polygon2):
        """ Calculate the intersection area of two polygons """
        poly1 = Polygon(polygon1)
        poly2 = Polygon(polygon2)
        intersection = poly1.intersection(poly2)
        return intersection.area
    
    def load_park_from_sql():
        global park_poly_pos,park_data,enter_data
        data = []       
        for row in cam2:
            if row[2] != '':
                data.append(row)
            else:
                enter_data.append(json.loads(row[4]))

        for row in data:
            id_value = row[0]
            point_value = eval(row[2]) if row[2] != '' else []
            park_data.append({"id": id_value, "polygon": point_value})
        
        enter_poly_pos = [np.array(shape['polygon'], np.int32) for shape in enter_data[0]]
        park_poly_pos = [np.array(shape['polygon'], np.int32) for shape in park_data]
        return park_data,enter_data
    

    def put_thai_text(image, text, position, font_path, font_size, color):
        image_pil = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, font=font, fill=color)
        image = cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
        return image
    # crop_plate = put_thai_text(crop_plate, letter_dic[str(cname)], (int(cpix[0]), int(cpix[1])),'THSarabunNew.ttf',32,(0, 255, 0))


    park_data=load_park_from_json('park.json')
    enter_data=load_park_from_json('enter.json')


    while True:
        print('this is top program')
        # if multi_variable.stop_threads:
        #     break
        try:
            print(plate_cross)
            timeNow = datetime.now().strftime("%H:%M %S | %d/%m/%Y")
            # print(f'{timeNow} time topppppppppppppppppppppppp')
            ret, pic = vdo.read()
            pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)

            # if multi_variable.finalword not in plate_cross:
            #     plate_cross.append(multi_variable.finalword)
            if not ret:
                print('Fail to read, trying to restart')
                break
                vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
                time.sleep(1)
                continue

            pic_de = pic.copy()
            
            frame_counter += 1
            if frame_counter % (skip_frames + 1) != 0:
                continue

            result = model.track(pic_de, conf=0.5, persist=1)

            overlay = pic.copy()
            copy_park_data = park_data.copy()
            id_inPark = []
            free_space = len(park_data)
            not_free_space = 0

            
            # turn enter to polygon
            enter_poly = Polygon(enter_data)  
            cv.fillPoly(overlay, [np.array(enter_poly.exterior.coords, np.int32)], purple)

            # turn park to poly
            for shape_data in park_data:
                park_polygon = np.array(shape_data['polygon'], np.int32)  # Ensure correct format
                park_poly = Polygon(park_polygon)  
                cv.fillPoly(overlay, [np.array(park_poly.exterior.coords, np.int32)], green)

            for x in result[0].boxes:
                name = result[0].names[int(x.cls)]
                pix = x.xyxy.tolist()[0]
                id = int(x.id)
                cls = int(x.cls)
                plate = None

                car_poly = Polygon([(pix[0], pix[1]),(pix[2], pix[1]),(pix[2], pix[3]),(pix[0], pix[3])])    
                cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

                enter_inter = polygon_intersection_area(enter_poly, car_poly)
                enter_area = polygon_area(enter_poly)
                enter_percentage = (enter_inter / enter_area) * 100

                if enter_percentage >= 30:
                    ajan[id] = True  # Mark car as tracked
                    plate = plate_cross[0] 
                    cv.fillPoly(overlay, [np.array(enter_poly.exterior.coords, np.int32)], red)
                    plate_cross.pop(0)
                else:
                    if id not in ajan:
                        ajan[id] = False
                        # plate = plate_cross[0] 
                        # cv.putText(pic, plate, (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

                if plate != None:
                    pic = put_thai_text(pic, plate, (int(pix[0]), int(pix[1])),'THSarabunNew.ttf',32,(0, 255, 0))

                # Parking space occupancy check
                for shape_data in park_data:
                    park_polygon = shape_data['polygon']
                    park_id = shape_data['id']

                    inter_area = polygon_intersection_area(park_polygon, car_poly)
                    pix_area = polygon_area(park_polygon)

                    # print(f'{ajan} ==============')
                    
                    if pix_area > 0:
                        overlap_percentage = (inter_area / pix_area) * 100
                        if overlap_percentage >= 30 and len(copy_park_data) > 0 and (not id in id_inPark):
                            matching_polygon_index = next((index for index, data in enumerate(copy_park_data) if data['id'] == shape_data['id']), None)
                            if matching_polygon_index is not None:
                                # print(f'car id {id} reserved {copy_park_data[matching_polygon_index]["id"]}')
                                not_free_space += 1
                                free_space -= 1
                                id_inPark.append(id)
                                if ajan.get(id, False) and cls ==2 or cls ==2 or cls ==7 :
                                    car_color = blue
                                    print(f'{cls} : {name} {car_color}')

                                if ajan.get(id, True) and cls ==2 :
                                    car_color = red
                                    print(f'{cls} : {name} {car_color}')

                                if cls != 2 and cls!=7 :
                                    car_color=yellow
                                    print(f'{cls} : {name} {car_color}')

                                cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], car_color)
                                copy_park_data.pop(matching_polygon_index)

            alpha = 0.5
            cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
            cv.putText(pic, 'FreeSpace: %s' % (str(free_space)), (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA)
            
            # pic = put_thai_text(pic, plate_cross, (50, 80),'THSarabunNew.ttf',32,(0, 255, 0))
            cv.putText(pic, f'{plate_cross}', (50, 80), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA)
            cv.imshow('Full Scene', pic)
            if cv.waitKey(1) & 0xFF == ord('q'):
                with open('multi_save.txt', 'w', encoding='utf-8') as file:
                    for x in range(plate_cross):
                        file.write(x)
                print(f'{plate_cross} this is plate cross')
                print(f'{len(plate_cross)} this is len plate cross')
                # multi_variable.stop_threads = True  # ตั้งค่า flag
                break

        except Exception as e:
            print(f'Error: {e}')
            break
    print(plate_cross)
    vdo.release()
    cv.destroyAllWindows()



def plateProgram(model,modelP,modelC):
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



    
    vdo = cv.VideoCapture('vdo_from_park/GF.mp4')
    # vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

    check = True
    check2 = True
    count = 0
    skip_frames = 15
    frame_counter = 0

    wordfull = ""
    car_id = []
    cross_car =[]
    id_cross = set()
    dataword = []
    plateName =''
    datacar_in_park = []
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
    multi =[]

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

        for db in car_row:
            matcher = difflib.SequenceMatcher(None, db[3], finalword)
            per = matcher.ratio() * 100

            if per > max_per:
                max_per = per
                best_word = db[3]

        print('++++++++++')
        print(finalword)

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

        if id not in car_hascross:
            car_hascross.append(id)
            # multi_variable.finalword = finalword
            # multi.append(multi_variable.finalword)
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

        print(finalword)
        print(f'{max_per} {best_word}')
        print('++++++++++')
   

        
        # print(f'{multi_variable.finalword}   this is multi variable')
        # print(f'{multi_variable.finalword} this is mult final')
        # # multi_variable.finalword = None

        

            

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
        # if multi_variable.stop_threads:
        #     break
        try:
            ret, pic = vdo.read()
            width = vdo.get(cv.CAP_PROP_FRAME_WIDTH)
            height = vdo.get(cv.CAP_PROP_FRAME_HEIGHT)
            timeNow = datetime.now().strftime("%H:%M %S | %d/%m/%Y")
            # print(f'{timeNow} time plateeeeeeeeeeeeeeeeeeeeeee')



            if not ret:
                break
                print('Fail to read, trying to restart')
                vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
                time.sleep(1)
                continue
            
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
                            
            # print(f'{timeNow} time plateeeeeeeeeeeeeeeeeeeeeee')
            if cv.waitKey(1) & 0xFF == ord('p'):
                break

        except Exception as e:
            print(f'Error: {e}')

    print('_______ ')
    print(f'{multi} this is multi')
    print(cross_car)
    print(f'id that has cross : {car_hascross}')
    print('_______ ')

    vdo.release()
    cv.destroyAllWindows()



# # ตัวแปรสำหรับหยุดเธรด
# multi_variable.stop_threads = False

model = YOLO('model/yolov8m.pt')
model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')


def run_plate_program():
    multi_plate_test.plateProgram()

def run_top_program():
    multi_top_test.topProgram()

plate_thread = threading.Thread(target=run_plate_program)
top_thread = threading.Thread(target=run_top_program)

plate_thread.start()
time.sleep(1)
top_thread.start()

plate_thread.join()
top_thread.join()

print("Both programs have completed.")
