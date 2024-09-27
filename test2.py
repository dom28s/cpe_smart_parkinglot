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
from flask import Response

# Additional function to stream video frames
def generate_video_stream():
    while True:
        if multi_variable.current_frame is not None:
            ret, buffer = cv.imencode('.jpg', multi_variable.current_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
                result = model.track(pic_de, conf=0.5, persist=3)

            # Your code for processing the image and overlay text
            pic = put_thai_text(pic, str(multi_variable.finalword['plate']), (50, 80), 'THSarabunNew.ttf', 48, (0, 255, 0))
            
            # Store the current frame in a global variable for streaming
            multi_variable.current_frame = pic

            # Display the frame locally (optional)
            cv.imshow('Full Scene', pic)
            if cv.waitKey(1) & 0xFF == ord('q'):
                multi_variable.stop_threads = True
                break

        except Exception as e:
            print(f'Error: {e}')
            break

    vdo.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    topProgram()
