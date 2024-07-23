from ultralytics import YOLO
import cv2 as cv
import pyautogui

model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
count =0

vdo = cv.VideoCapture('vdo_from_park/G7.mp4')

while True:
    x, y = pyautogui.position()
    i, pic = vdo.read()
    if not i:
        print("Failed to read frame. Exiting...")
        break

    pic = cv.resize(pic, (1260, 860))
    result_model = model(pic, conf=0.5, classes=2)
    print(result_model)

    for e in result_model[0].boxes:
        name = result_model[0].names[int(e.cls)]
        pix = e.xyxy.tolist()[0]  # Convert tensor to list and access the first element

        cv.putText(pic, "%s %.2f" % (str(name), float(e.conf)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

        crop_car = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
        resultP = modelP(crop_car,conf=0.5)

        for x in resultP[0].boxes:
            pname = resultP[0].names[int(x.cls)]
            ppix = x.xyxy.tolist()[0]
            cv.rectangle(crop_car, (int(ppix[0]), int(ppix[1])), (int(ppix[2]), int(ppix[3])), (255, 0, 0), 2)

            crop_plate = crop_car[int(ppix[1]):int(ppix[3]), int(ppix[0]):int(ppix[2])]
            crop_plate = cv.resize(crop_plate,(560,250))

            resultC = modelC(crop_plate,conf=0.5)

            for y in resultC[0].boxes:
                cname = resultC[0].names[int(y.cls)]
                cpix = y.xyxy.tolist()[0]

                cv.putText(crop_plate, "%s %.2f" % (str(cname), float(y.conf)), (int(cpix[0]), int(cpix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv.rectangle(crop_plate, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)
                cv.imshow('df',crop_plate)

    cv.imshow('test', pic)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

vdo.release()
cv.destroyAllWindows()
