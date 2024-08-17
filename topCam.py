from ultralytics import YOLO
import cv2 as cv


model = YOLO('model/yolov10l.pt')

vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
vdo = cv.VideoCapture('vdo_from_park/topCam.mp4')

frame_counter = 0
skip_frames = 15

cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

while True:
    ret, pic = vdo.read()
   
    pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)

    frame_counter += 1
    if frame_counter % (skip_frames + 1) != 0:
        continue

    result = model.track(pic,conf=0.5,persist=1,)

    for x in result[0].boxes:
        name = result[0].names[int(x.cls)]
        pix = x.xyxy.tolist()[0]
        id = int(x.id)

        cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

    cv.imshow('Full Scene', pic)
    if cv.waitKey(1) & 0xFF == ord('p'):
        break
vdo.release()
cv.destroyAllWindows()


