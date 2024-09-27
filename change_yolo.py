from deepsparse import Pipeline
from ultralytics import YOLO

# โหลดโมเดล YOLO (เช่น yolov5 หรือ yolov8)
model_path = 'model/yolov8n.onnx'  # ใช้ไฟล์ ONNX ที่เข้ากันกับ DeepSparse

# สร้าง DeepSparse pipeline
pipeline = Pipeline.create(task="yolo", model_path=model_path)

# ทำการตรวจจับวัตถุ
image_path = 'images/cat.jpg'
output = pipeline(images=[image_path])

# แสดงผลการตรวจจับ
print(output)
