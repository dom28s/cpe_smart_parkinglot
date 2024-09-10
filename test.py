import cv2
from super_gradients.training import models
from super_gradients.common.object_names import Models

# โหลดโมเดล YOLO-NAS
model = models.get(Models.YOLO_NAS_S, pretrained_weights="coco")

# โหลดไฟล์วิดีโอ
video_path = "vdo_from_park/G7.mp4"
cap = cv2.VideoCapture(video_path)

# ตรวจสอบว่าทำการโหลดวิดีโอสำเร็จหรือไม่
if not cap.isOpened():
    print("Error: ไม่สามารถเปิดวิดีโอได้")
    exit()

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    # ทำการตรวจจับวัตถุในเฟรมปัจจุบัน
    predictions = model.predict(frame)

    # วาดกล่องรอบวัตถุที่ตรวจจับได้
    for box in predictions[0].pred_boxes_xyxy:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # แสดงผลเฟรมที่ตรวจจับ
    cv2.imshow("YOLO-NAS Detection", frame)

    # กด 'q' เพื่อออกจากการแสดงผล
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปล่อยทรัพยากร
cap.release()
cv2.destroyAllWindows()
