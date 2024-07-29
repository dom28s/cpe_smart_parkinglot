from ultralytics import YOLO
import cv2 as cv
import pyautogui
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

with open('class.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
count =0
vdo = cv.VideoCapture('vdo_from_park/G7.mp4')
ret, pic = vdo.read()
wordfull = ""

park = []
line =[]

check =True
cap = cv.VideoWriter()
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

def mouse_click(event, x, y, flags, param,):
    global check,line,park
    if event == cv.EVENT_LBUTTONDOWN:
        line.append([x, y])
        print(line)
        cv.putText(pic2, f'{x} {y}', (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if len(line) == 2:
            cv.line(pic2, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)

    if event == cv.EVENT_RBUTTONDOWN:
        check = False

def letterCheck():
    global wordfull

    max = 0
    datamax = 0
    for x in range(len(dataword)):
        if len(dataword[x]) > datamax:
            max = x
            datamax = len(dataword[x])
    for x in range(len(dataword[max])):
        for j in range(len(dataword[max])):
            if dataword[max][x][1] < dataword[max][j][1]:
                t = dataword[max][x]
                dataword[max][x] = dataword[max][j]
                dataword[max][j] = t
    wordfull = ""
    for x in dataword[max]:
        wordfull += x[0]+" "
    print(wordfull)


# def put_text_utf8(image, text, position, font_size=30, color=(0, 255, 0)):
#     """Draw UTF-8 text on an OpenCV image using Pillow."""
#     pil_img = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
#     draw = ImageDraw.Draw(pil_img)
#     font = ImageFont.truetype('arial.ttf', font_size)  # Ensure this font file supports UTF-8
#     draw.text(position, text, font=font, fill=color)
#     return cv.cvtColor(np.array(pil_img), cv.COLOR_RGB2BGR)


pic2 = pic.copy()

while check:
    x, y = pyautogui.position()
    cv.imshow("Full Scene",pic2)
    cv.setMouseCallback('Full Scene', mouse_click)
    if cv.waitKey(1) & 0xFF == ord('p'):
        break


dataword = []

while True:
    ret, pic = vdo.read()
    if not ret:
        print("Failed to read frame. Exiting...")
        break

    cv.line(pic, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)
    result_model = model.track(pic, conf=0.5, classes=2,persist=True)

    print(dataword)

    for e in result_model[0].boxes:
        name = result_model[0].names[int(e.cls)]
        pix = e.xyxy.tolist()[0]  # Convert tensor to list and access the first element
        id = e.id.tolist()
        print('tihs is id')
        print(id)

        if pix[0] > 500:
            cv.putText(pic, "%s  %.0f" % (str(name), float(e.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)
            print(result_model[0].boxes)

            crop_car = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
            resultP = modelP(crop_car, conf=0.5)

            for x in resultP[0].boxes:
                pname = resultP[0].names[int(x.cls)]
                ppix = x.xyxy.tolist()[0]

                cv.rectangle(crop_car, (int(ppix[0]), int(ppix[1])), (int(ppix[2]), int(ppix[3])), (255, 0, 0), 2)

                crop_plate = crop_car[int(ppix[1]):int(ppix[3]), int(ppix[0]):int(ppix[2])]
                crop_plate = cv.resize(crop_plate, (560, 250))

                resultC = modelC(crop_plate, conf=0.5)

                if ppix[0] + pix[0] <= line[0][0] and ppix[2] + pix[0] <= line[0][0]:
                    # pic = put_text_utf8(pic, wordfull, (904, 632), font_size=30, color=(0, 255, 0))
                    cv.putText(pic, "dd", (904, 632), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


                wordf = []
                for y in resultC[0].boxes:
                    mode = True
                    cname = resultC[0].names[int(y.cls)]
                    cpix = y.xyxy.tolist()[0]
                    try:
                        if len(data[str(cname)]) > 2:
                            wordf.append([data[str(cname)], 10000])
                        else:
                            wordf.append([data[str(cname)], cpix[0]])
                        print(wordf)
                    except KeyError:
                        print("Key not found in data dictionary")
                    cv.putText(crop_plate,(str(cname)), (int(cpix[0]), int(cpix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv.rectangle(crop_plate, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)
                    print(data[cname])
                    cv.imshow('df', crop_plate)
                if len(wordf) != 0:
                    dataword.append(wordf.copy())




    cv.imshow('Full Scene', pic)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

letterCheck(mode)

vdo.release()
cv.destroyAllWindows()




