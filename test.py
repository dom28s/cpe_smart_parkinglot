import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from shapely.ops import unary_union
from ultralytics import YOLO

# โหลดโมเดล YOLO
model = YOLO('model/yolov8n.pt')

# เปิดกล้อง
vdo = cv.VideoCapture(0)  

frame_counter = 0
skip_frames = 7
check = True

# ตั้งค่าหน้าต่างสำหรับการแสดงผล
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# กำหนดสีสำหรับแสดงผล
green = (0, 255, 0)  # ว่าง
red = (0, 0, 255)    # ไม่ว่าง
yellow = (0, 255, 255)  # ความจุไม่แน่นอน

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
            save_park_to_json('line_test.json')  # Save polygons after adding a new one


def polygon_area(polygon):
    """ คำนวณพื้นที่ของพอลิกอน """
    return Polygon(polygon).area

def polygon_intersection_area(polygon1, polygon2):
    """ คำนวณพื้นที่ทับซ้อนของพอลิกอนสองอัน """
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    intersection = poly1.intersection(poly2)
    return intersection.area

# โหลดพอลิกอนจากไฟล์ JSON
load_park_from_json('line_test.json')
ret,pic = vdo.read()

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
            break

        pic = cv.flip(pic, 1)  # พลิกภาพจากซ้ายไปขวา
        pic_de = pic.copy()
        
        frame_counter += 1
        if frame_counter % (skip_frames + 1) != 0:
            continue

        result = model.track(pic_de, conf=0.5, persist=1, classes=67)
        overlay = pic.copy()
        copy_park_data = park_data.copy()
        id_inPark = []

        for x in result[0].boxes:
            name = result[0].names[int(x.cls)]
            pix = x.xyxy.tolist()[0]
            id = int(x.id)

            # แสดงชื่อและ ID ของวัตถุที่ตรวจพบ
            cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), green, 2)

            # แปลงขอบเขตของวัตถุเป็นพอลิกอนสำหรับคำนวณทับซ้อน
            pix_polygon = [[pix[0], pix[1]], [pix[2], pix[1]], [pix[2], pix[3]], [pix[0], pix[3]]]

            for shape_data in park_data:
                park_polygon = shape_data['polygon']

                inter_area = polygon_intersection_area(park_polygon, pix_polygon)
                pix_area = polygon_area(park_polygon)
                if pix_area > 0:
                    overlap_percentage = (inter_area / pix_area) * 100
                    print(f'{id} {overlap_percentage}')

                    if overlap_percentage >= 30 and len(copy_park_data) > 0 and (not id in id_inPark):
                        cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], red) 
                        copy_park_data.remove(park_polygon)
                        if id not in id_inPark:
                            id_inPark.append(id)
                    else:
                        cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], green)

                    # หาจุดบนสุดของพอลิกอนเพื่อแสดงเปอร์เซ็นต์การทับซ้อน
                    top_left = min(park_polygon, key=lambda p: p[1])  # หาจุดที่มี y น้อยที่สุด
                    cv.putText(pic, f"{int(overlap_percentage)}%", (top_left[0], top_left[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 1, yellow, 2)

        # วาด ID ตรงกลางพอลิกอน
        for shape_data in park_data:
            park_polygon = shape_data['polygon']
            park_id = shape_data['id']

            # คำนวณจุดศูนย์กลางพอลิกอนเพื่อแสดง ID
            poly = Polygon(park_polygon)
            centroid = poly.centroid.coords[0]
            cv.putText(pic, f"ID {park_id}", (int(centroid[0]), int(centroid[1])), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2)

        alpha = 0.5
        cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print(f'Error: {e}')
        
vdo.release()
cv.destroyAllWindows()
