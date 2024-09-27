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
from flask import Flask, Response

# Initialize Flask app
app = Flask(__name__)

def topProgram():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="projects2"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `parkingspace`")
    cam2 = cursor.fetchall()
    plate_cross =[]
    
    with open('class.json', 'r', encoding='utf-8') as file:
        letter_dic = json.load(file)
        
    model = YOLO('model/yolov8l.pt')
    vdo = cv.VideoCapture('vdo_from_park/top.mp4')
    frame_counter = 0
    skip_frames = 20
    check = True

    # Define colors for display
    green = (0, 255, 0)  # Available
    red = (0, 0, 255)    # Occupied
    yellow = (0, 255, 255)  # Obstacle
    blue = (255, 0, 0)   # บุคคลภายนอก
    purple = (128, 0, 128)

    park_data = []
    enter_data = []
    frame_count = 0
    car_track = {"is_ajan": [], "plate": [], "id": []}

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
        return Polygon(polygon).area

    def polygon_intersection_area(polygon1, polygon2):
        poly1 = Polygon(polygon1)
        poly2 = Polygon(polygon2)
        intersection = poly1.intersection(poly2)
        return intersection.area

    def put_thai_text(image, text, position, font_path, font_size, color):
        image_pil = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, font=font, fill=color)
        image = cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
        return image

    park_data = load_park_from_json('park.json')
    enter_data = load_park_from_json('enter.json')

    while True:
        if multi_variable.stop_threads:
            break
        try:
            ret, pic = vdo.read()
            if not ret:
                vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
                time.sleep(1)
                continue

            pic_de = pic.copy()
            frame_counter += 1
            if frame_counter % (skip_frames + 1) != 0:
                continue
            if frame_count % 60 == 0:
                result = model.track(pic_de, conf=0.5, persist=3,)

            overlay = pic.copy()
            copy_park_data = park_data.copy()
            id_inPark = []
            free_space = len(park_data)
            not_free_space = 0

            enter_poly = Polygon(enter_data)
            cv.fillPoly(overlay, [np.array(enter_poly.exterior.coords, np.int32)], purple)

            for shape_data in park_data:
                park_polygon = np.array(shape_data['polygon'], np.int32)
                park_poly = Polygon(park_polygon)
                cv.fillPoly(overlay, [np.array(park_poly.exterior.coords, np.int32)], green)

            for x in result[0].boxes:
                name = result[0].names[int(x.cls)]
                pix = x.xyxy.tolist()[0]
                id = int(x.id)
                cls = int(x.cls)

                car_poly = Polygon([(pix[0], pix[1]), (pix[2], pix[1]), (pix[2], pix[3]), (pix[0], pix[3])])

                if id in car_track['id']:
                    sel_id = car_track['id'].index(id)
                    plate_number = car_track['plate'][sel_id]
                    pic = put_thai_text(pic, plate_number, (int(pix[0]), int(pix[1])), 'THSarabunNew.ttf', 48, (0, 255, 0))
                else:
                    cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

            alpha = 0.5
            cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
            pic = put_thai_text(pic, str(multi_variable.finalword['plate']), (50, 80), 'THSarabunNew.ttf', 48, (0, 255, 0))

            ret, buffer = cv.imencode('.jpg', pic)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f'Error: {e}')
            break

    vdo.release()
    cv.destroyAllWindows()


@app.route('/video_feed')
def video_feed():
    return Response(topProgram(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
