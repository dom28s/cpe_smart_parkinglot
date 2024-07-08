
from ultralytics import YOLO
import random
import cv2
import numpy as np

model = YOLO("yolov8m-seg.pt")
img = cv2.imread("images/parking_lot_1.png")

results = model.predict(img, 0.5)

for x in results:
    for mask, box in zip(x.masks.xy, x.boxes):
        points = np.int32([mask])
        cv2.polylines(img, points, True, (255, 0, 0), 1)
        cv2.fillPoly(img, points, (255,255,255,),0)

cv2.imshow("Image", img)
cv2.waitKey(0)




