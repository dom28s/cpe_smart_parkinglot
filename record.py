import cv2
import time
import os
from datetime import datetime

vdo = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

count =0

while True:
    ret, pic = vdo.read()
    time.sleep(1)
    count+=1
    if count%10 ==0 :
        count=0
        current_time = datetime.now()
        day= current_time.strftime('%d-%m-%Y')  # Format: YYYY-MM-DD
        hour= current_time.strftime('%H%M')  # Format: HH (24-hour format)
        sec=current_time.strftime('%S')
        save_dir = f'picSave/{day}/{hour}'

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filename = f'{hour}{sec}.jpg'
        cv2.imwrite(f'{save_dir}/{filename}', pic)
        print(f"Saved: {filename}")
    if cv2.waitKey(1) & 0xFF == ord('p'):
        break

# Release resources
vdo.release()
cv2.destroyAllWindows()
