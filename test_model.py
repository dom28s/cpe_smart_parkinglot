from ultralytics import YOLO
import cv2 as cv
import time

# Load YOLO models
model = YOLO('model/yolov8n.pt')
# plate11 = YOLO('model/plate11m.pt')
plate11 = YOLO('model/licen_100b.pt')

# Open video file
vdo = cv.VideoCapture('vdo_from_park/plate.mp4')
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# Start timer
start_time = time.time()

prev_time = 0
fps_list = []  # List to store FPS values
detection_count = 0  # Counter for object detections
plate_count = 0  # Counter for detected license plates

while True:
    ret, pic = vdo.read()

    if not ret:
        break

    # Calculate FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    # Add current FPS to the list
    fps_list.append(fps)

    # Perform object tracking
    result_model = model.track(pic, conf=0.5, classes=2, persist=True)

    # If any objects are detected, increment the detection counter
    if len(result_model[0].boxes) > 0:
        detection_count += 1

    for e in result_model[0].boxes:
        name = result_model[0].names[int(e.cls)]
        pix = e.xyxy.tolist()[0]

        # Crop car image
        crop_car = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]

        # Perform plate detection
        plate11_results = plate11(crop_car, conf=0.5)

        for i in plate11_results[0].boxes:
            ppix = i.xyxy.tolist()[0]
            # Draw bounding box for detected license plate
            cv.rectangle(pic, 
                         (int(ppix[0]) + int(pix[0]), int(ppix[1]) + int(pix[1])), 
                         (int(ppix[2]) + int(pix[0]), int(ppix[3]) + int(pix[1])), 
                         (0, 0, 255), 2)
            # Increment plate detection count
            plate_count += 1

    # Display FPS on the video frame
    cv.putText(pic, "FPS: %.2f" % fps, (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show full scene with FPS
    cv.imshow('Full Scene', pic)

    # Exit loop when 'p' is pressed
    if cv.waitKey(1) & 0xFF == ord('p'):
        break

# End timer
end_time = time.time()
elapsed_time = end_time - start_time  # Calculate elapsed time

# Calculate and print average FPS
avg_fps = sum(fps_list) / len(fps_list)
print("Average FPS: %.2f" % avg_fps)

# Print total object detections and license plate detections
print("Total object detections: %d" % detection_count)
print("Total license plates detected: %d" % plate_count)

# Print elapsed time
print("Total time taken: %.2f seconds" % elapsed_time)

# Release video and destroy all windows
vdo.release()
cv.destroyAllWindows()
