from ultralytics import YOLO
import cv2 as cv
import pyautogui

model = YOLO('model/yolov8l.pt')

vdo = cv.VideoCapture('videos/cpe_fscam.mp4')



while True:
    x,y = pyautogui.position()
    i,pic = vdo.read()
    result_model = model(pic,conf=0.5,classes = 2)

    for e in result_model[0].boxes:
        name = result_model[0].names[int(e.cls)]
        pix = e.xyxy[0].tolist()
        print(x,y)

        cv.putText(pic,"%s %.2f"%(str(name),(float(e.conf))),(int(pix[0]),int(pix[1])),cv.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv.rectangle(pic, (int(pix[0]),int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

    cv.imshow('test',pic)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

vdo.release()
cv.destroyAllWindows()