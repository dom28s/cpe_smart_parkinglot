from ultralytics import YOLO
import cv2
import numpy as np

# โหลดโมเดล
# Nmodel = YOLO('model/best_numberchar_50.pt')

Cmodel = YOLO('model/thaiChar_100b.pt')
Lmodel = YOLO('model/licen_100b.pt')

# โหลดภาพ
pic = cv2.imread('images/plate4.jpg')
pic = cv2.imread('images/platetest20.png')


# เพิ่มความคมชัดให้กับภาพ
# kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
# sharpened_pic = cv2.filter2D(pic, -1, kernel)

# ตรวจจับวัตถุในภาพที่มีการเพิ่มความคมชัด
result = Lmodel(pic, conf=0.5)

# วาดกรอบและชื่อวัตถุที่ตรวจจับได้บนภาพ
for x in result[0].boxes:
    name = Lmodel.names[int(x.cls)]
    pix = x.xyxy[0].tolist()

    cv2.putText(pic, "%s %.2f" % (str(name), float(x.conf)), (int(pix[0]), int(pix[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

    # ครอบภาพและขยายขนาดภาพที่ครอบ
    cropped_pic = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
    cropped_pic = cv2.resize(cropped_pic, (640, 480))
    
    resultC = Cmodel(cropped_pic,conf=0.5)
    print(resultC)

    for y in resultC[0].boxes:
        cname = resultC[0].names[int(y.cls)]

        cpix = y.xyxy.tolist()[0]

        cv2.putText(cropped_pic, "%s" % (str(cname)), (int(cpix[0]), int(cpix[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(cropped_pic, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)


        # แสดงภาพที่ครอบและขยายขนาดแล้ว
# cv2.imshow("dfd",cropped_pic)

# แสดงภาพที่ตรวจจับและวาดกรอบ
cv2.imshow('Result', pic)
cv2.waitKey(0)
cv2.destroyAllWindows()