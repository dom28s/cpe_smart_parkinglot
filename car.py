from ultralytics import YOLO
import cv2 as cv
import pyautogui

model = YOLO('model/yolov8l.pt')
pointer = []
line = []

vdo = cv.VideoCapture('vdo_from_park/topCam2.mp4')

i,pic = vdo.read()

cv.namedWindow('frame', cv.WINDOW_NORMAL)
cv.setWindowProperty('frame', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

current_x = 0
current_y = 0
park = []
i =0

while True:
    pic2 = pic.copy()
    cv.putText(pic2,str(str(current_x) +" "+ str(current_y)),(0,50),cv.FONT_HERSHEY_SIMPLEX,(2),(255,0,0),2)

    
    for y in park:
        for x in y:
            cv.line(pic2,(x[0][0],x[0][1]),(x[1][0],x[1][1]),(255,0,0),2)
    cv.imshow("frame",pic2)
    
    if cv.waitKey(0) & 0xFF == ord('s'):
        current_x, current_y = pyautogui.position()
        pointer.append([current_x-1920, current_y])
        if len(pointer)==2:
            line.append(pointer.copy())
            pointer = []
        if len(line) == 2:
            park.append(line.copy())
            line = []
    if cv.waitKey(0) & 0xFF == ord('q'):
        break
     

while True:
    notem=[]   
    ret, frame = vdo.read()
    if not ret:
        break

    frame = cv.resize(frame,(1920,1080))
    results = model(frame,conf=0.5)


    for x in results[0].boxes:          #car
        name = results[0].names[int(x.cls)]
        pix = x.xyxy[0].tolist()

        for i in park:   #left top #left bottom #
            if (pix[0] > i[0][0][0] and pix[0] < i[0][1][0]) and (pix[2] > i[1][0][0] and pix[2] < i[1][1][0]):
                notem.append(i)
         
                

        cv.putText(frame,"%s %.2f"%(str(name),(float(x.conf))),(int(pix[0]),int(pix[1])),cv.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv.rectangle(frame, (int(pix[0]),int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)
    c=0
    for y in park:
        c+=1
        if y in notem:
            for x in y:
                cv.line(frame,(x[0][0],x[0][1]),(x[1][0],x[1][1]),(0,0,255),2)
            cv.putText(frame,str(c),((((y[1][0][0] - y[0][0][0])//2)+y[0][0][0]),(((x[1][1] - x[0][1])//2)+x[0][1])),cv.FONT_HERSHEY_SIMPLEX,2,(0,0,255),2)
            continue
        for x in y:
            cv.line(frame,(x[0][0],x[0][1]),(x[1][0],x[1][1]),(255,0,0),2)
        cv.putText(frame,str(c),((((y[1][0][0] - y[0][0][0])//2)+y[0][0][0]),(((x[1][1] - x[0][1])//2)+x[0][1])),cv.FONT_HERSHEY_SIMPLEX,2,(0,255,0),2)

        

    cv.imshow("frame", frame)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

vdo.release()
cv.destroyAllWindows()

