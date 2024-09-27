import cv2 as cv
from ultralytics import YOLOWorld

# เปิดวิดีโอ
cap = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

frame_count = 0
skip_frames = 5  # จำนวนเฟรมที่ต้องการทิ้ง

cv.namedWindow('Full', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)


model = YOLOWorld("yolov8l-world.pt")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # ทิ้งเฟรมทุกๆ 5 เฟรม
    if frame_count % skip_frames == 0:
        result = model.track(frame, conf=0.5, persist=3)

    frame_count += 1

    # แสดงเฟรมปัจจุบัน (สามารถเลือกที่จะไม่แสดงผลได้เพื่อเพิ่มความเร็ว)
    cv.imshow('Full', frame)

    # ออกจากลูปเมื่อกดปุ่ม 'q'
    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
