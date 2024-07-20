from ultralytics import YOLO
import threading
import cv2 as cv
import time
import pyautogui

# Load the YOLO model
model = YOLO('model/yolov8l.pt')
Lmodel = YOLO('model/licenplate.pt')
NModel = YOLO('model/number.pt')
vdo = cv.VideoCapture('vdo_from_park/G7.mp4')
frame = None


def getFrame():
    global vdo,frame
    count = 0
    while True:
        if count %6 != 0:
            count +=1
            time.sleep(0.010)
            continue
        else:
            count +=1
            time.sleep(0.010)

        ret, frame = vdo.read()
        if not ret:
            print("Failed to read frame. Exiting...")
            break

def detect():
    global vdo,frame,Lmodel,NModel,model
    while True:
        result = model(frame,conf=0.5)
        for f in result[0].boxes:
            fname = result[0].names[int(f.cls)]
            fpos = f.xyxy.tolist()
            cv.putText(frame, "%s %.2f" % (str(fname), (float(f.conf))), (int(fpos[0]),int(fpos[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(frame, (int(fpos[0]), int(fpos[1])), (int(fpos[2]), int(fpos[3])), (0, 255, 0), 2)





        Lresult = Lmodel(frame, conf=0.5)
        if frame is None:
            continue
        for i, x in enumerate(Lresult[0].boxes):
            name = Lresult[0].names[int(x.cls)]
            pix = x.xyxy[0].tolist()

            cv.putText(frame, "%s %.2f" % (str(name), (float(x.conf))), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(frame, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

            cropped_pic = frame[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
            Nresult = NModel(cropped_pic,conf=0.5)

            for i in Nresult[0].boxes:
                Nname = Nresult[0].names[int(i.cls)]
                Npix = i.xyxy[0].tolist()

                cv.putText(cropped_pic, "%s" % str(Nname), (int(Npix[0]), int(Npix[1])), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv.rectangle(cropped_pic, (int(Npix[0]), int(Npix[1])), (int(Npix[2]), int(Npix[3])), (0, 255, 0), 1)
        

def show():
    global frame
    while True:
        mx,my = pyautogui.position()
        cv.putText(frame, str(mx)+' '+str(my), (10,50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        if frame is None:
            continue
        frame = cv.resize(frame,(1280,720))
        cv.imshow('dd',frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            vdo.release()
            cv.destroyAllWindows()
            break

if __name__ == "__main__":
    getFrame_th = threading.Thread(target=getFrame)
    detect_th = threading.Thread(target=detect)
    show_th = threading.Thread(target=show)

    getFrame_th.daemon =True
    detect_th.daemon =True
    show_th.daemon =True

    getFrame_th.start()
    detect_th.start()
    show_th.start()

    getFrame_th.join()
    detect_th.join()
    show_th.join()


