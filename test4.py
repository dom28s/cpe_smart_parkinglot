from ultralytics import YOLO
import cv2 as cv
import json

vdo = cv.VideoCapture(0)
model = YOLO('model/yolov8n.pt')
check = True
allline =[]

try:
    with open('linetest.json', 'r') as f:
        allline = json.load(f)
except FileNotFoundError:
    allline = []

def mouse_click(event, x, y, flags, param):
    global check, linetest, allline
    if event == cv.EVENT_LBUTTONDOWN:
        linetest.append([x, y])
        cv.putText(pic2, f'{x} {y}', (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if len(linetest) == 2:
            cv.line(pic2, (linetest[0][0], linetest[0][1]), (linetest[1][0], linetest[1][1]), (255, 0, 255), 5)
            allline.append(linetest.copy())
            linetest.clear()

            if (len(allline)) ==2:
                with open('linetest.json', 'w') as f:
                    json.dump(allline, f)
                check = False
    if event == cv.EVENT_RBUTTONDOWN:
        check = False

def is_line_intersecting_bbox(bbox, line):
    x1, y1, x2, y2 = bbox
    (x3, y3), (x4, y4) = line

    edges = [
        ((x1, y1), (x2, y1)),  # Top
        ((x2, y1), (x2, y2)),  # Right
        ((x2, y2), (x1, y2)),  # Bottom
        ((x1, y2), (x1, y1))   # Left
    ]

    for edge in edges:
        if do_intersect(edge, line):
            return True
    return False

def do_intersect(line1, line2):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    (A, B), (C, D) = line1, line2
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

ret, pic = vdo.read()
pic2 = pic.copy()
if len(allline) < 2:
    while check:
        cv.imshow("Full Scene", pic2)
        cv.setMouseCallback('Full Scene', mouse_click)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
print(allline)
while True:
    try:
        ret, pic = vdo.read()
        pic = cv.flip(pic, 1)
        
        result_model = model.track(pic, conf=0.4, classes=0, persist=True)
        
        for e in result_model[0].boxes:
            name = result_model[0].names[int(e.cls)]
            pix = e.xyxy.tolist()[0]

            bbox = (int(pix[0]), int(pix[1]), int(pix[2]), int(pix[3]))
            line1 = ((allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]))
            line2 = ((allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]))ๅ

            cv.putText(pic, "%s  %.0f" % (str(name), float(e.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)
            
            if is_line_intersecting_bbox(bbox, line1):
                cv.putText(pic, "hit", (10, 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            else:
                cv.line(pic, (allline[0][0][0], allline[0][0][1]), (allline[0][1][0], allline[0][1][1]), (255, 0, 255), 5)
                cv.line(pic, (allline[1][0][0], allline[1][0][1]), (allline[1][1][0], allline[1][1][1]), (255, 0, 255), 5)


        cv.imshow('sdsd', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print('Error:', str(e))

cv.destroyAllWindows()
