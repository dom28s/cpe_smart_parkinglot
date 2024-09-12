import cv2 as cv
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.116:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
while True:
    
        ret, pic = vdo.read()
        if not ret:
            break
        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break