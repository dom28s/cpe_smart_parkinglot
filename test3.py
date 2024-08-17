from ultralytics import YOLO
import cv2 as cv
import numpy as np

model = YOLO('model/yolov8l.pt')

# vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
vdo = cv.VideoCapture('vdo_from_park/topCam.mp4') # Uncomment this line if using a video file

frame_counter = 0
skip_frames = 15

cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# color definitions
green = (0, 255, 0)  # empty
red = (0, 0, 255)    # not empty
blue = (255, 0, 0)   # unknown
yellow = (0, 255, 255)  # undefined occupancy

# Variables for drawing
points = []
park =[]
max_points = 4
start_point = None
check = True

def draw_shape(event, x, y, flags, param):
    global  points, start_point, check,park
    if event == cv.EVENT_LBUTTONDOWN:
            points.append((x,y))
            print(points)
            if len(points) == max_points:
                points.append(points[0]) 
                park.append(points.copy())
                points.clear()


ret, pic = vdo.read()
pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)

while check:
    cv.imshow("Full Scene", pic)
    cv.setMouseCallback('Full Scene', draw_shape)

    if len(park) >0:  # Polygon is closed with 4 points + 1 to close
        overlay = pic.copy()
        for shape in park:
            points_array = np.array(shape, np.int32)  # Convert list of points to NumPy array
            points_array = points_array.reshape((-1, 1, 2))  # Reshape for fillPoly
            cv.fillPoly(overlay, [points_array], yellow)
        alpha = 0.5  # Transparency level
        pic2 = cv.addWeighted(pic, 1 - alpha, overlay, alpha, 0)
        cv.imshow("Full Scene", pic2)
        cv.waitKey(0)
        check = False  # Exit the drawing loop after completing one shape

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

while True:
    ret, pic = vdo.read()
    if not ret:
        break

    pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)
    pic_de = pic.copy()
    overlay = pic.copy()
    for shape in park:
            points_array = np.array(shape, np.int32)  # Convert list of points to NumPy array
            points_array = points_array.reshape((-1, 1, 2))  # Reshape for fillPoly
            cv.fillPoly(overlay, [points_array], yellow)
            alpha = 0.5  # Transparency level
            pic = cv.addWeighted(pic, 1 - alpha, overlay, alpha, 0)

    frame_counter += 1
    if frame_counter % (skip_frames + 1) != 0:
        continue

    result = model.track(pic_de, conf=0.5, persist=1)

    for x in result[0].boxes:
        name = result[0].names[int(x.cls)]
        pix = x.xyxy.tolist()[0]
        id = int(x.id)

        cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
        cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), green, 2)

    cv.imshow('Full Scene', pic)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break


vdo.release()
cv.destroyAllWindows()
