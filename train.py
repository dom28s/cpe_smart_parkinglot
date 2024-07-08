from ultralytics import YOLO

# เป็นการสร้างโมเดลใหม่ขึ้นมา
model = YOLO('yolov8n.yaml')

# โหลด pretrained model มาเพื่อให้เราไม่ต้องเทรนใหม่ทั้งหมดตั้งแต่เริ่ม
model = YOLO('model/yolov8n.pt')

# เทรนโมเดลโดยใช้ datasets ของเรา ซึ่งให้เราหาไฟล์ data.yaml 
# ในโฟลเดอร์ Datasets ของเราเเล้วเอา Path มาวางตรง data=
# แนะนำว่าให้เอา Path ทั้งหมดมาเลย
# epoch = 3 คือเราเทรนทั้งหมด 3 รอบ
path = '/Users/Thanawat/Documents/RMUTT/year 4/Project/data/LPR plate.v2i.yolov8/data.yaml'
results = model.train(data=path, epochs=3)

#gpu train
# results = model.train(data=path, epochs=3, device='cuda')

# ทดสอบโมเดลโดยใช้ validation datasets ที่เตรียมไว้
results = model.val()

# เซฟโมเดลโดยให้โมเดลอยู่ใน ONNX format
success = model.export(format='onnx')