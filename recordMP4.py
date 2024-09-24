import cv2

# เปิดกล้อง (0 หมายถึงกล้องตัวแรกของเครื่อง)
vdo1 = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
vdo2 = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

# ตรวจสอบว่ากล้องถูกเปิดสำเร็จหรือไม่
if not vdo1.isOpened():
    print("ไม่สามารถเปิดกล้อง vdo1 ได้")
    exit()
if not vdo2.isOpened():
    print("ไม่สามารถเปิดกล้อง vdo2 ได้")
    exit()

# ตั้งค่าการบันทึกวิดีโอ (ชื่อไฟล์, Codec, FPS, ขนาดเฟรม)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
top = cv2.VideoWriter('top.mp4', fourcc, 24.0, (1920, 1080))
plate = cv2.VideoWriter('plate.mp4', fourcc, 24.0, (1920, 1080))

try:
    while True:
        # อ่านเฟรมจากกล้อง
        ret, frame = vdo1.read()
        ret2, frame2 = vdo2.read()

        # ตรวจสอบว่าอ่านสำเร็จหรือไม่
        if not ret:
            print("ไม่สามารถอ่านเฟรมจากกล้อง vdo1 ได้")
            break
        if not ret2:
            print("ไม่สามารถอ่านเฟรมจากกล้อง vdo2 ได้")
            break

        # เขียนเฟรมลงในไฟล์วิดีโอ
        top.write(frame)     # เขียนเฟรมจากกล้อง vdo1 ลงในไฟล์ top.mp4
        plate.write(frame2)  # เขียนเฟรมจากกล้อง vdo2 ลงในไฟล์ plate.mp4
except KeyboardInterrupt:
    print("การบันทึกวิดีโอหยุดโดยผู้ใช้")

finally:
    # ปล่อยกล้องและปิด VideoWriter
    vdo2.release()
    vdo1.release()
    top.release()
    plate.release()
