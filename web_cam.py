import cv2
from ultralytics import YOLO

model = YOLO('model/yolov8n.pt')

# Replace the URL with the URL of your IP Webcam stream
url = "http://192.168.1.153:8080/video"


cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    result = model(frame,conf=0.5)
    
    for x in result[0].boxes:
        name = result[0].names[int(x.cls)]
        pix = x.xyxy[0].tolist()

        cv2.putText(frame,"%s %.2f"%(str(name),(float(x.conf))),(int(pix[0]),int(pix[1])),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv2.rectangle(frame, (int(pix[0]),int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

    cv2.imshow('frame',frame)
    
    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
