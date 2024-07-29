from ultralytics import YOLO
import cv2 as cv
import pyautogui
import json

with open('class.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


model = YOLO('model/yolov8n.pt')
modelP = YOLO('model/licen_100b.pt')
modelC = YOLO('model/thaiChar_100b.pt')
count =0
vdo = cv.VideoCapture('vdo_from_park/G7.mp4')
ret, pic = vdo.read()

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

def licenCheck(mode):
    
    mode = False
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
    



pic2 = pic.copy()

while check:
    x, y = pyautogui.position()
    cv.imshow("Full Scene",pic2)
    cv.setMouseCallback('Full Scene', mouse_click)
    if cv.waitKey(1) & 0xFF == ord('p'):
        break


dataword = []
mode = False
while True:
    ret, pic = vdo.read()
    if not ret:
        print("Failed to read frame. Exiting...")
        break

    cv.line(pic, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (255, 0, 255), 5)

 
    result_model = model.track(pic, conf=0.5, classes=2,persist=True)

    print(dataword)

    # In the main processing loop
    for e in result_model[0].boxes:
        name = result_model[0].names[int(e.cls)]
        pix = e.xyxy.tolist()[0]  # Convert tensor to list and access the first element

        if pix[0] > 500:
            cv.putText(pic, "%s %.2f" % (str(name), float(e.conf)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

            crop_car = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
            resultP = modelP(crop_car, conf=0.5)

            for x in resultP[0].boxes:
                pname = resultP[0].names[int(x.cls)]
                ppix = x.xyxy.tolist()[0]

                cv.rectangle(crop_car, (int(ppix[0]), int(ppix[1])), (int(ppix[2]), int(ppix[3])), (255, 0, 0), 2)

                crop_plate = crop_car[int(ppix[1]):int(ppix[3]), int(ppix[0]):int(ppix[2])]
                crop_plate = cv.resize(crop_plate, (560, 250))

                resultC = modelC(crop_plate, conf=0.5)

                # Debugging information
                

                # Corrected condition logic
                if ppix[0] + pix[0] <= line[0][0] and ppix[2] + pix[0] <= line[0][0]:
                    cv.putText(pic, "YOUNGOHM MATAFAKKA", (904, 632), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

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
                    cv.putText(crop_plate, "%s %.1f" % (str(cname), float(y.conf)), (int(cpix[0]), int(cpix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv.rectangle(crop_plate, (int(cpix[0]), int(cpix[1])), (int(cpix[2]), int(cpix[3])), (0, 255, 0), 1)
                    print(data[cname])
                    cv.imshow('df', crop_plate)
                if len(wordf) != 0:
                    dataword.append(wordf.copy())
                    mode = True



    cv.imshow('Full Scene', pic)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

licenCheck(mode)

vdo.release()
cv.destroyAllWindows()




