from ultralytics import YOLO
import cv2

model = YOLO('model/yolov8l.pt')
vdo = cv2.VideoCapture('vdo_from_park/topCam2.mp4')

frameCount =1
frameSkip = 3

while True:
    ret,pic = vdo.read()
    frame = cv2.resize(pic,(640,384))
    result = model(frame,conf=0.5)

    frameCount +=1
    if frameCount % frameSkip!=0:
        continue

    for x in result[0].boxes:
        name = result[0].names[int(x.cls)]
        pos = x.xyxy[0].tolist()

        cv2.putText(frame,str(name),(int(pos[0]),int(pos[1])),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv2.rectangle(frame,(int(pos[0]),int(pos[1])),(int(pos[2]),int(pos[3]),),(255,0,0),1,1)

    cv2.imshow('d',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break 

cv2.destroyAllWindows()
vdo.release()
