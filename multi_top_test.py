import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from ultralytics import YOLO
import time
import multi_variable
from datetime import datetime


def topProgram():
    plate_cross =[]
    with open('class.json', 'r', encoding='utf-8') as file:
        letter_dic = json.load(file)

    # while multi_variable.finalword == None:
    #     time.sleep(1)
    #     continue

    # if multi_variable.finalword != None:
    #     print('44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444')
    #     print('44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444')
    #     print('44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444')
    #     print(f"finalword send {multi_variable.finalword}\n\n\n\n\n\n")
    #     plate_cross.append(multi_variable.finalword)
    #     multi_variable.finalword = None
    #     print(f"finalword send {multi_variable.finalword}\n\n\n\n\n\n")

    print('===========================================================================================================================================================================\n=====================================================================\n======================================================')
    while multi_variable.finalword == None:
        time.sleep(1)
        continue
    print(f"finalword send {multi_variable.finalword}\n\n\n\n\n\n\n")
    plate_cross.append(multi_variable.finalword)
    print(f'{plate_cross} plateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' )
    multi_variable.finalword = None
    while multi_variable.finalword == None:
        time.sleep(1)
        continue
    print(f"finalword send {multi_variable.finalword}\n\n\n\n\n\n")
  
        
    model = YOLO('model/yolov8m.pt')

    vdo = cv.VideoCapture('vdo_from_park/topCam.mp4')

    frame_counter = 0
    skip_frames = 7
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

    park_data=load_park_from_json('park.json')
    enter_data=load_park_from_json('enter.json')


    while True:
        if multi_variable.stop_threads:
            break
        try:
            print(plate_cross)
            timeNow = datetime.now().strftime("%H:%M %S | %d/%m/%Y")
            # print(f'{timeNow} time topppppppppppppppppppppppp')
            ret, pic = vdo.read()
            pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)


            if not ret:
                print('Fail to read, trying to restart')
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

                car_poly = Polygon([(pix[0], pix[1]),(pix[2], pix[1]),(pix[2], pix[3]),(pix[0], pix[3])])    
                cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)

                enter_inter = polygon_intersection_area(enter_poly, car_poly)
                enter_area = polygon_area(enter_poly)
                enter_percentage = (enter_inter / enter_area) * 100

                if enter_percentage >= 30:
                    ajan[id] = True  # Mark car as tracked
                    # print(f'{id} entered, percent {enter_percentage}')
                    cv.fillPoly(overlay, [np.array(enter_poly.exterior.coords, np.int32)], red)
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
                                car_color = red if ajan.get(id, False) else blue
                                cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], car_color)
                                copy_park_data.pop(matching_polygon_index)

            alpha = 0.5
            cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
            cv.putText(pic, 'FreeSpace: %s' % (str(free_space)), (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA)
            cv.putText(pic, f'{plate_cross}', (50, 80), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2, cv.LINE_AA)

            cv.imshow('Full Scene', pic)
            if cv.waitKey(1) & 0xFF == ord('q'):
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