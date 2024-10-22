import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from ultralytics import YOLO
import time
import multi_variable
from datetime import datetime
import mysql.connector
from PIL import ImageFont, ImageDraw, Image




def topProgram():
    conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password ="admin",
    database="projects"

    # host="100.124.147.43",
    # user="admin",
    # password ="admin",
    # database="projects"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `parkingspace`")
    cam2 = cursor.fetchall()
    plate_cross =[]
    with open('class.json', 'r', encoding='utf-8') as file:
        letter_dic = json.load(file)
        
    model = YOLO('model/yolov8l.pt')

    vdo = cv.VideoCapture('vdo_from_park/top.mp4')
    vdo = cv.VideoCapture('vdo_from_park/topCam.mp4')

    frame_counter = 0
    skip_frames = 20
    check = True


    cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    # Define colors for display
    green = (0, 255, 0)  # Available
    red = (0, 0, 255)    # Occupied
    yellow = (0, 255, 255)  # Obstacle
    blue = (255,0,0) #บุคคลภายนอก
    purple = (128, 0, 128)

  
    park_data = []

    enter_data = []
   
    frame_count = 0

    car_track = {
        "is_ajan":[],
        "plate":[],
        "id":[]
    }
    

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
    
    def load_from_sql():
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

        return enter_data,park_data
    

    def put_thai_text(image, text, position, font_path, font_size, color):
        image_pil = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, font=font, fill=color)
        image = cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
        return image
    # crop_plate = put_thai_text(crop_plate, letter_dic[str(cname)], (int(cpix[0]), int(cpix[1])),'THSarabunNew.ttf',32,(0, 255, 0))


    # park_data=load_park_from_json('park.json')
    # enter_data=load_park_from_json('enter.json')
    enter_data,park_data = load_from_sql()

    


    while True:
        if multi_variable.stop_threads:
            break
        try:
            ret, pic = vdo.read()
            pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)
            
                
            if not ret:
                print('Fail to read, trying to restart')
                # break
                vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
                time.sleep(1)
                continue

            pic_de = pic.copy()
            
            frame_counter += 1
            if frame_counter % (skip_frames + 1) != 0:
                continue
            if frame_count % 60 == 0:  # ประมวลผลทุกๆ 3 เฟรม
                result = model.track(pic_de, conf=0.5, persist=3,)

            overlay = pic.copy()
            copy_park_data = park_data.copy()
            id_inPark = []
            free_space = len(park_data)
            blue_park = 0
            red_park =0
            yellow_park =0

            
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

                car_poly = Polygon([(pix[0], pix[1]),(pix[2], pix[1]),(pix[2], pix[3]),(pix[0], pix[3])])    

                

                if id in car_track['id']:
                    sel_id = car_track['id'].index(id)  # หา index ของ id
                    plate_number = car_track['plate'][sel_id]  # ดึง plate ตาม index
                    pic = put_thai_text(pic, plate_number, (int(pix[0]), int(pix[1])), 'THSarabunNew.ttf', 48, (0, 255, 0))
                else:
                    cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

                

                enter_inter = polygon_intersection_area(enter_poly, car_poly)
                enter_area = polygon_area(enter_poly)
                enter_percentage = (enter_inter / enter_area) * 100

                # just car NEED TO FIX LATER
                if enter_percentage >= 30:
                    
                        for ajan_value, plate_value in zip(multi_variable.finalword['ajan'], multi_variable.finalword['plate']):
                            # ใช้ ajan_value โดยตรง
                            if id not in car_track['id']:
                                car_track['id'].append(id)
                                car_track['is_ajan'].append(ajan_value)  # ใช้มันโดยตรง
                                car_track['plate'].append(plate_value)    # ใช้มันโดยตรง
                                if plate_value in multi_variable.finalword['plate']:
                                    multi_variable.finalword['plate'].remove(plate_value)


                        cv.fillPoly(overlay, [np.array(enter_poly.exterior.coords, np.int32)], red)
                cv.putText(pic, str(car_track), (10,200), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
  

                # Parking space occupancy check
                for shape_data in park_data:
                    park_polygon = shape_data['polygon']
                    park_id = shape_data['id']

                    inter_area = polygon_intersection_area(park_polygon, car_poly)
                    pix_area = polygon_area(park_polygon)

                    # print(f'{ajan} ==============')
                    
                    if pix_area > 0:  
                        overlap_percentage = (inter_area / pix_area) * 100  
                        if overlap_percentage >= 30 and len(copy_park_data) > 0 and id not in id_inPark:
                            matching_polygon_index = None
                            for index in range(len(copy_park_data)):
                                if copy_park_data[index]['id'] == shape_data['id']:
                                    matching_polygon_index = index
                                    break


                            if matching_polygon_index is not None:
                                free_space -= 1
                                id_inPark.append(id)

                                print(car_track)
                                if car_track["id"] and car_track["is_ajan"]:
                                    print(car_track['id'])
                                    print(car_track['is_ajan'])
                                    
                                    for x in car_track["id"]:
                                        if x in id_inPark:
                                            k = car_track['id'].index(x)  # หา index ของ id
                                            
                                            if k < len(car_track["is_ajan"]):  # ตรวจสอบว่า index ไม่เกินขอบเขต
                                                if car_track["is_ajan"][k] == True:
                                                    print(car_track["is_ajan"])
                                                    print('======')
                                                    car_color = red
                                                    red_park+=1
                                                    break  # Exit the loop since we've set the color

                                                if car_track["is_ajan"][k] == False:
                                                    car_color = blue
                                                    blue_park+=1
                                                    break  # Exit the loop since we've set the color

                                # Check if the id is not in the car_track to set the color based on cls
                                if id not in car_track["id"]:  # Change this to `id` from `id_inPark`
                                    if cls == 2 or cls == 7:  # Corrected to check cls
                                        car_color = blue
                                        blue_park+=1
                                        
                                    else:
                                        yellow_park +=1
                                        car_color = yellow

                                print(f'yeloow {yellow_park}')
                                print(f'red {red_park}')
                                print(f'blue {blue_park}')
                                print(f'green {free_space}')
                                cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], car_color)
                                copy_park_data.pop(matching_polygon_index)  # Remove the polygon from the available list


            alpha = 0.5
            cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
            cv.putText(pic, f'Green {str(free_space)}', (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA)
            cv.putText(pic, f'Blue {str(blue_park)}', (50, 80), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA) 
            cv.putText(pic, f'Red: {str(red_park)}', (50, 120), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA) 
            cv.putText(pic, f'Yellow: {str(yellow_park)}', (50, 150), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA) 
            if len(plate_cross ) != 0:
                pic = put_thai_text(pic, str(plate_cross), (50, 80),'THSarabunNew.ttf',48,(0, 255, 0))
            pic = put_thai_text(pic, str(multi_variable.finalword['plate']), (50, 80),'THSarabunNew.ttf',48,(0, 255, 0))
            cv.imshow('Full Scene', pic)
            print(' top pro')
            if cv.waitKey(1) & 0xFF == ord('q'):
                with open('multi_save.txt', 'w', encoding='utf-8') as file:
                    for x in range(plate_cross):
                        file.write(x)
                print(f'{plate_cross} this is plate cross')
                print(f'{len(plate_cross)} this is len plate cross')
                multi_variable.stop_threads = True  # ตั้งค่า flag
                break

        except Exception as e:
            print(f'Error: {e}')
            break
    print(plate_cross)
    vdo.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    topProgram()