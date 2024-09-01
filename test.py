import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from shapely.ops import unary_union
from ultralytics import YOLO

# โหลดโมเดล YOLO
model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
vdo = cv.VideoCapture('vdo_from_park/GF.mp4')
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

# เปิดกล้อง
vdo = cv.VideoCapture(0)  

frame_counter = 0
skip_frames = 7

# ตั้งค่าหน้าต่างสำหรับการแสดงผล
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# กำหนดสีสำหรับแสดงผล
green = (0, 255, 0)  # ว่าง
red = (0, 0, 255)    # ไม่ว่าง
blue = (255, 0, 0)   # ไม่ทราบ
yellow = (0, 255, 255)  # ความจุไม่แน่นอน

points = []  # เก็บพ้อยที่ใช้ในการวาดพอลิกอน
park = []    # เก็บพอลิกอนที่ระบุพื้นที่จอดรถ
max_points = 4  # จำนวนพ้อยสูงสุดที่ใช้ในการวาดพอลิกอน
check = True

def load_park_from_json(filename):
    """ โหลดพอลิกอนจากไฟล์ JSON """
    global park
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            park_data = json.load(f)
            park = [np.array(shape, np.int32) for shape in park_data]

def save_park_to_json(filename):
    """ บันทึกพอลิกอนลงในไฟล์ JSON """
    park_data = []
    for shape in park:
        park_data.append([[int(p[0]), int(p[1])] for p in shape])
    with open(filename, 'w') as f:
        json.dump(park_data, f)

def draw_shape(event, x, y, flags, param):
    """ ฟังก์ชันสำหรับวาดพอลิกอนโดยการคลิกเมาส์ """
    global points, park
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(points)
        if len(points) == max_points:
            points.append(points[0])  # ปิดพอลิกอน
            park.append(np.array(points, np.int32))  # แปลงเป็น NumPy array
            points.clear()
            save_park_to_json('test.json')  # บันทึกพอลิกอนหลังจากเพิ่มใหม่

load_park_from_json('test.json')  # โหลดพอลิกอนจากไฟล์ JSON

def polygon_area(polygon):
    """ คำนวณพื้นที่ของพอลิกอน """
    return Polygon(polygon).area

def polygon_intersection_area(polygon1, polygon2):
    """ คำนวณพื้นที่ทับซ้อนของพอลิกอนสองอัน """
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    intersection = poly1.intersection(poly2)
    return intersection.area

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

        result = model.track(pic_de, conf=0.5, persist=1, classes=0)

        overlay = pic.copy()

        for x in result[0].boxes:
            name = result[0].names[int(x.cls)]
            pix = x.xyxy.tolist()[0]
            id = int(x.id)

            # แสดงชื่อและ ID ของวัตถุที่ตรวจพบ
            cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), green, 2)

            # แปลงขอบเขตของวัตถุเป็นพอลิกอนสำหรับคำนวณทับซ้อน
            pix_polygon = [[pix[0], pix[1]], [pix[2], pix[1]], [pix[2], pix[3]], [pix[0], pix[3]]]

            for shape in park:
                park_polygon = shape.reshape((-1, 2)).tolist()

                # คำนวณพื้นที่ทับซ้อน
                inter_area = polygon_intersection_area(park_polygon, pix_polygon)

                # คำนวณพื้นที่ของพอลิกอน pix
                pix_area = polygon_area(pix_polygon)

                # คำนวณเปอร์เซ็นต์การทับซ้อน
                if pix_area > 0:
                    overlap_percentage = (inter_area / pix_area) * 100

                    # เปลี่ยนสีเป็นสีเหลืองหากเปอร์เซ็นต์การทับซ้อน >= 30%
                    if overlap_percentage >= 30:
                        cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], red)  # สีเหลือง
                    else:
                        cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], green)  # สีแดง

                    # แสดงเปอร์เซ็นต์การทับซ้อนที่กลางหน้าจอ
                    cv.putText(pic, "Overlap: %.2f%%" % overlap_percentage, (int(pix[0]),int(pix[1])),
                            cv.FONT_HERSHEY_SIMPLEX, 1, yellow, 2)
                else:
                    cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], red)  # สีแดง

        alpha = 0.5
        # รวมภาพ overlay และภาพหลัก
        cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)

        # แสดงภาพ
        cv.imshow('Full Scene', pic)

        # ออกจากลูปเมื่อกดปุ่ม 'p'
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print(f'Error: {e}')
        
vdo.release()
cv.destroyAllWindows()
