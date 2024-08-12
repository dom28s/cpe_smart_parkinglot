from ultralytics import YOLO
import cv2 as cv


model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
vdo = cv.VideoCapture('vdo_from_park/topCam.mp4')



while True:
    ret, pic = vdo.read()
    pic = cv.flip(pic, 0)
    cv.imshow('Full Scene', pic)
    if cv.waitKey(1) & 0xFF == ord('p'):
        break
vdo.release()
cv.destroyAllWindows()


