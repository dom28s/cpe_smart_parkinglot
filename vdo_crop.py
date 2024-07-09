from ultralytics import YOLO
import cv2 as cv

# Load the YOLO model
Lmodel = YOLO('model/licenplate.pt')
NModel = YOLO('model/number.pt')


# Open the video file
vdo = cv.VideoCapture('videos/cpe_scam.mp4')

while True:
    ret, frame = vdo.read()

    if not ret:
        print("Failed to read frame. Exiting...")
        break

    Lresult = Lmodel(frame, conf=0.5)
    

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


        # gray = cv.cvtColor(cropped_pic, cv.COLOR_BGR2GRAY)
        # gray = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]


        cv.imshow('d', cropped_pic)
        

    cv.imshow('Annotated Image', frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
vdo.release()
cv.destroyAllWindows()
