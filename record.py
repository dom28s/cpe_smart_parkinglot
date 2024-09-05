import cv2
import time
import os

# Create the folder if it doesn't exist
if not os.path.exists('picSave'):
    os.makedirs('picSave')

vdo = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

last_save_time = time.time()

while True:
    ret, pic = vdo.read()
    print(last_save_time)
    if ret:
        cv2.imshow('ff', pic)

        # Save a picture every 10 seconds
        if time.time() - last_save_time >= 10:
            filename = f'vdoSave/frame_{int(time.time())}.jpg'
            cv2.imwrite(filename, pic)
            last_save_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('p'):
        break

vdo.release()
cv2.destroyAllWindows()
