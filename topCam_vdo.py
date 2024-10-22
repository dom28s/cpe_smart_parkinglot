import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from ultralytics import YOLO
import time

with open('class.json', 'r', encoding='utf-8') as file:
    letter_dic = json.load(file)
    
model = YOLO('model/yolov8m.pt')

# vdo = cv.VideoCapture('vdo_from_park/top.mp4')
vdo = cv.VideoCapture('vdo_from_park/topCam.mp4')
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')




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
park_poly_pos = []    
park_data = []
park_id = 0  

enter_data = []
enter_poly=[]
check = True  

ajan ={}

def load_park_from_json(filename):
    global park_poly_pos, park_data, park_id, enter_data,enter_poly
    if os.path.exists(filename):
        if filename == 'park_real.json':
            with open(filename, 'r') as f:
                park_data = json.load(f)
                park_poly_pos = [np.array(shape['polygon'], np.int32) for shape in park_data]
                if park_data:
                    park_id = max([shape['id'] for shape in park_data]) + 1 

        if filename == 'enter_real.json':
            with open(filename, 'r') as f:
                enter_data = json.load(f)
                enter_poly = [np.array(polygon, np.int32) for polygon in enter_data]  # แปลงเป็น NumPy array
                print(f'Loaded enter_data: {enter_data}') 


def save_park_to_json(filename):
    global park_data, enter_data
    if filename == 'park_real.json':
        with open(filename, 'w') as f:
            json.dump(park_data, f)

    if filename == 'enter_real.json':
        with open(filename, 'w') as f:
            json.dump(enter_data[0], f)  # บันทึกทั้งลิสต์ enter_data
            print(f'Saving enter_data: {enter_data[0]}')

            
def draw_shape(event, x, y, flags, param):
    global points, park_poly_pos, park_id, park_data
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x, y))
        if len(points) == 4:
            points.append(points[0])  # Close the polygon
            park_poly_pos.append(np.array(points, np.int32))  # Convert to NumPy array
            park_data.append({
                'id': park_id,
                'polygon': [list(p) for p in points]
            })
            park_id += 1  
            points.clear()
            save_park_to_json('park_real.json')  # Save polygons after adding a new one

def draw_enter(event, x, y, flags, param):
    global points, enter_data, check,enter_poly
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(points)
        print(f'{len(points)} this is len point')
        if len(points) == 4:
            points.append(points[0])  
            enter_data.append(points.copy())
            enter_poly.append(np.array(points, np.int32))
            print(f'{enter_data[0]} enter data')  
            save_park_to_json('enter.json')  
            points.clear()  

def polygon_area(polygon):
    """ Calculate the area of a polygon """
    return Polygon(polygon).area

def polygon_intersection_area(polygon1, polygon2):
    """ Calculate the intersection area of two polygons """
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    intersection = poly1.intersection(poly2)
    return intersection.area

load_park_from_json('park_real.json')
load_park_from_json('enter.json')

ret, pic = vdo.read()
# pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)

while check:
    cv.imshow("Full Scene", pic)
    cv.setMouseCallback('Full Scene', draw_shape)
    
    if len(park_poly_pos) > 0:  
        overlay = pic.copy()
        for shape in park_poly_pos:
            points_array = shape.reshape((-1, 1, 2))  
            cv.fillPoly(overlay, [points_array], green)
        alpha = 0.5 
        pic2 = cv.addWeighted(pic, 1 - alpha, overlay, alpha, 0)
        cv.imshow("Full Scene", pic2)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

check = True 

while check:
    cv.putText(pic2, "enter" , (10,10), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
    cv.imshow("Full Scene", pic2)
    # print(enter_poly)
    try:
        print(f'{enter_data[0]} len {len(enter_data[0])}')
    except:
        print('')

    print(f'{len(enter_data)} ------------')
    if len(enter_data)==0:
        cv.setMouseCallback('Full Scene', draw_enter)

    if len(enter_data) == 5: 
        print(f'len enter = {len(enter_data)}')
        overlay = pic2.copy()
        for shape in enter_poly:
            points_array = shape.reshape((-1, 1, 2))  
            cv.fillPoly(overlay, [points_array], yellow)
        alpha = 0.5  
        pic2 = cv.addWeighted(pic2, 1 - alpha, overlay, alpha, 0)
        cv.imshow("Full Scene", pic2)
        print('break')
        check = False
        break

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

while True:
    try:
        ret, pic = vdo.read()
        # pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)

        if not ret:
            print('Fail to read, trying to restart')
            vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
            time.sleep(5)

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
        # print(result)

        # turn enter to polygon
        if len(enter_data) >= 3:
            enter_box = Polygon(enter_data)  
            cv.fillPoly(overlay, [np.array(enter_box.exterior.coords, np.int32)], purple)

        # Process park polygons
        for shape_data in park_data:
            park_polygon = np.array(shape_data['polygon'], np.int32)  # Ensure correct format
            fill_park = Polygon(park_polygon)  
            cv.fillPoly(overlay, [np.array(fill_park.exterior.coords, np.int32)], green)

        for x in result[0].boxes:
            name = result[0].names[int(x.cls)]
            cls = int(x.cls)      #add
            pix = x.xyxy.tolist()[0]
            id = int(x.id)
            # 2 =car 
            # 7 = truck
            # 0 = person
            # 1 = bicycle
            # 3 = mortorcy
            # 5 = bus


            car_poly = Polygon([(pix[0], pix[1]),(pix[2], pix[1]),(pix[2], pix[3]),(pix[0], pix[3])])    


            cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

            if len(enter_data) >= 3:
                enter_inter = polygon_intersection_area(enter_box, car_poly)
                enter_area = polygon_area(enter_box)
                enter_percentage = (enter_inter / enter_area) * 100

                if enter_percentage >= 30:
                    ajan[id] = True  # Mark car as tracked
                    print(f'{id} entered, percent {enter_percentage}')
                    cv.fillPoly(overlay, [np.array(enter_box.exterior.coords, np.int32)], red)
                else:
                    if id not in ajan:
                        ajan[id] = False
            # Parking space occupancy check
            for shape_data in park_data:
                park_polygon = shape_data['polygon']
                park_id = shape_data['id']

                inter_area = polygon_intersection_area(park_polygon, car_poly)
                pix_area = polygon_area(park_polygon)

                # print(f'{ajan} ==============')
                
                if pix_area > 0:
                    overlap_percentage = (inter_area / pix_area) * 100
                    # print(f'{id} overlap percentage {overlap_percentage}')

                    if overlap_percentage >= 30 and len(copy_park_data) > 0 and (not id in id_inPark):
                        matching_polygon_index = next((index for index, data in enumerate(copy_park_data) if data['id'] == shape_data['id']), None)
                        if matching_polygon_index is not None:
                            # print(f'car id {id} reserved {copy_park_data[matching_polygon_index]["id"]}')
                            not_free_space += 1
                            free_space -= 1
                            id_inPark.append(id)
                            car_color = (255,255,255)

                            # ADD
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

        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f'Error: {e}')
        break

vdo.release()
cv.destroyAllWindows()
