import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from shapely.ops import unary_union
from ultralytics import YOLO
import time

# โหลดโมเดล YOLO
model = YOLO('model/yolov8l.pt')

# เปิดกล้อง
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')


frame_counter = 0
skip_frames = 7
check = True

# ตั้งค่าหน้าต่างสำหรับการแสดงผล
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# กำหนดสีสำหรับแสดงผล
green = (0, 255, 0)  # ว่าง
red = (0, 0, 255)    # ไม่ว่าง
yellow = (0, 255, 255)  # สิ่งกีดขวาง
blue = (255,0,0) #บุตตลภายนอก

points = []  # เก็บพ้อยที่ใช้ในการวาดพอลิกอน
park_poly_pos = []    # เก็บพอลิกอนที่ระบุพื้นที่จอดรถ
park_data = []
park_id = 0  # ID สำหรับพอลิกอนใหม่

def load_park_from_json(filename):
    global park_poly_pos, park_data, park_id
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            park_data = json.load(f)
            park_poly_pos = [np.array(shape['polygon'], np.int32) for shape in park_data]
            if park_data:
                park_id = max([shape['id'] for shape in park_data]) + 1  # ตั้งค่า park_id เป็นค่าถัดไป


def save_park_to_json(filename):
    global park_data 
    with open(filename, 'w') as f:
        json.dump(park_data, f)


def draw_shape(event, x, y, flags, param):
    global points, park_poly_pos, park_id, park_data
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x, y))
        if len(points) == 4:
            points.append(points[0])  # Close the polygon
            park_poly_pos.append(np.array(points, np.int32))  # Convert to NumPy array
            # เพิ่มข้อมูลพอลิกอนพร้อมกับ ID
            park_data.append({
                'id': park_id,
                'polygon': [list(p) for p in points]
            })
            park_id += 1  # เพิ่ม ID สำหรับพอลิกอนถัดไป
            points.clear()
            save_park_to_json('park.json')  # Save polygons after adding a new one


def polygon_area(polygon):
    """ คำนวณพื้นที่ของพอลิกอน """
    return Polygon(polygon).area

def polygon_intersection_area(polygon1, polygon2):
    """ คำนวณพื้นที่ทับซ้อนของพอลิกอนสองอัน """
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    intersection = poly1.intersection(poly2)
    return intersection.area


load_park_from_json('park.json')


ret, pic = vdo.read()

while check:
    cv.imshow("Full Scene", pic)
    cv.setMouseCallback('Full Scene', draw_shape)
    if len(park_poly_pos) > 0:  # Draw polygons on the image
        overlay = pic.copy()
        for shape in park_poly_pos:
            points_array = shape.reshape((-1, 1, 2))  # Ensure corparkt shape for fillPoly
            cv.fillPoly(overlay, [points_array], yellow)
        alpha = 0.5  # Transparency level
        pic2 = cv.addWeighted(pic, 1 - alpha, overlay, alpha, 0)
        cv.imshow("Full Scene", pic2)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

while True:
    try:
        ret, pic = vdo.read()

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

        # Draw all parking spaces first
        for shape_data in park_data:
            park_polygon = shape_data['polygon']
            cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], green)

        for x in result[0].boxes:
            name = result[0].names[int(x.cls)]
            pix = x.xyxy.tolist()[0]
            id = int(x.id)

            cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
            pix_polygon = [[pix[0], pix[1]], [pix[2], pix[1]], [pix[2], pix[3]], [pix[0], pix[3]]]

            for shape_data in park_data:
                park_polygon = shape_data['polygon']
                park_id = shape_data['id']

                inter_area = polygon_intersection_area(park_polygon, pix_polygon)
                pix_area = polygon_area(park_polygon)
                if pix_area > 0:
                    overlap_percentage = (inter_area / pix_area) * 100
                    print(f'{id} {overlap_percentage}')

                    if overlap_percentage >= 30 and len(copy_park_data) > 0 and (not id in id_inPark):
                        matching_polygon_index = next((index for index, data in enumerate(copy_park_data) if data['id'] == shape_data['id']), None)
                        if matching_polygon_index is not None:
                            # Color the parking space as occupied
                            cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], red)
                            copy_park_data.pop(matching_polygon_index)
                            id_inPark.append(id)
                            not_free_space+=1
                            free_space -=1

                    # Display overlap percentage
                    top_left = min(park_polygon, key=lambda p: p[1])
                    cv.putText(pic, f"{int(overlap_percentage)}%", (top_left[0], top_left[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 1, yellow, 2)

        # Display the parking space ID in the center of the polygon
        for shape_data in park_data:
            park_polygon = shape_data['polygon']
            park_id = shape_data['id']
            poly = Polygon(park_polygon)
            centroid = poly.centroid.coords[0]
            cv.putText(pic, f"ID {park_id}", (int(centroid[0]), int(centroid[1])), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2)

        # Display free and occupied space counts
        cv.putText(pic, f"free spaces: {free_space}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2)
        cv.putText(pic, f"not free spaces: {not_free_space}", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

        # Blend the overlay with the original image
        alpha = 0.5
        cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
        cv.imshow('Full Scene', pic)
        print(f'\nfree: {free_space}')
        print(f'not free: {not_free_space}')

        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print(f'Error: {e}')

        
vdo.release()
cv.destroyAllWindows()

