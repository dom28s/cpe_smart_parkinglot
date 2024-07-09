from ultralytics import YOLO
import cv2 as cv

model = YOLO('model/yolov8n.pt')

vdo = cv.VideoCapture('videos/cpe_fcam.mp4')


while True:
    i,pic = vdo.read()
    result_model = model(pic,conf=0.5)

    for x in result_model[0].boxes:
        name = result_model[0].names[int(x.cls)]
        pix = x.xyxy[0].tolist()

        cv.putText(pic,"%s %.2f"%(str(name),(float(x.conf))),(int(pix[0]),int(pix[1])),cv.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv.rectangle(pic, (int(pix[0]),int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

    cv.imshow('test',pic)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

vdo.release()
cv.destroyAllWindows()