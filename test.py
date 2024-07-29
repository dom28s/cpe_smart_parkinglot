
import cv2

from ultralytics import YOLO


model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture('vdo_from_park/G7.mp4')


while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True)

        for x in results[0].boxes:
            name = results[0].names[int(x.cls)]
            pos = x.xyxy.tolist()[0]
            id = x.id.tolist()

            cv2.rectangle(frame,(int(pos[0]),int(pos[1])),(int(pos[2]),int(pos[3])),(255,0,0),2,)
            cv2.putText(frame,name+str(id),(int(pos[0]),int(pos[1])),cv2.FONT_HERSHEY_SIMPLEX,(2),(255,0,0),2)
            


        cv2.imshow("YOLOv8 Tracking",frame)


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()