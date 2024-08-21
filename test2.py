import cv2 as cv
from ultralytics import YOLO
import json
import numpy as np

# Load YOLO models
model = YOLO('model/yolov8n.pt')

# Load video
vdo = cv.VideoCapture('vdo_from_park/GS.mp4')

# Initialize variables for tracking
trackers = cv.MultiTracker_create()
track_ids = {}
tracker_id = 0
direction_lines = []

while True:
    ret, frame = vdo.read()
    if not ret:
        break

    # Object detection
    result_model = model(frame, conf=0.5, classes=2)
    detections = result_model[0].boxes

    # Update trackers
    success, boxes = trackers.update(frame)

    # Draw direction lines
    for line in direction_lines:
        cv.line(frame, line[0], line[1], (0, 255, 0), 2)

    for box in detections:
        name = result_model[0].names[int(box.cls)]
        pix = box.xyxy.tolist()[0]

        # Create a new tracker for the detected car
        tracker = cv.TrackerKCF_create()
        bbox = (int(pix[0]), int(pix[1]), int(pix[2]) - int(pix[0]), int(pix[3]) - int(pix[1]))
        trackers.add(tracker, frame, bbox)

        # Draw detection bounding box
        cv.putText(frame, "%s " % str(name), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.rectangle(frame, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

    # Draw tracking bounding boxes
    for i, box in enumerate(boxes):
        p1 = (int(box[0]), int(box[1]))
        p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
        cv.rectangle(frame, p1, p2, (255, 0, 0), 2)
        
        # Calculate and draw direction if necessary
        # Assuming you have a function to check if a car passed a specific region
        if car_passed_region(p1, p2):
            direction_line = ((p1[0], p1[1]), (p2[0], p2[1]))
            direction_lines.append(direction_line)
            cv.line(frame, direction_line[0], direction_line[1], (0, 255, 255), 2)

    # Display results
    cv.imshow('Car Tracking and Direction', frame)
    
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

vdo.release()
cv.destroyAllWindows()

def car_passed_region(p1, p2):
    # Implement logic to determine if the car has passed a specific region
    # This function should return True if the car has passed the region
    return False
