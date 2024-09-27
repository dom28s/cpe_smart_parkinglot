import cv2
from deepsparse import Pipeline
from deepsparse.yolo.schemas import YOLOInput

# Define the path to the ONNX model
model_path = 'model/yolov8n.onnx'  # Use the ONNX file compatible with DeepSparse

# Create DeepSparse pipeline
pipeline = Pipeline.create(task="yolo", model_path=model_path)

# Start capturing video from the camera
# cap = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
cap = cv2.VideoCapture('vdo_from_park/G7.mp4')

frames_processed = 0
start_time = cv2.getTickCount()
fps = 0.0  # Initialize fps variable

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to the format expected by DeepSparse
    input_data = YOLOInput(images=[frame])

    # Process the image using the DeepSparse pipeline
    detections = pipeline(input_data)

    # Draw bounding boxes on the frame
    for detection in detections:
        boxes = detection.boxes  # Get the boxes from the detection
        print(f"Boxes: {boxes}")  # Debug print to check the box structure
        for box in boxes:
            print(f"Box data: {box}")  # Print individual box data
            
            # Unpack the box values based on the actual structure
            if len(box) == 4:  # Assuming structure is [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, box)
                conf = None  # Set default or handle differently if needed
                label_index = None  # Set default or handle differently if needed
            elif len(box) == 6:  # If the structure has confidence and class index
                x1, y1, x2, y2, conf, label_index = box
            else:
                print(f"Unexpected box structure: {box}")
                continue  # Skip this box if the structure is unexpected

            # Handle confidence and label name
            if conf is not None and label_index is not None:
                conf = float(conf)
                label_name = detection.names[label_index] if hasattr(detection, 'names') else f'Class {label_index}'
                label = f'{label_name} {conf:.2f}'  # Class label with confidence

                # Draw the bounding box and label on the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw box
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Calculate and display FPS
    frames_processed += 1
    if frames_processed % 10 == 0:  # Every 10 frames
        elapsed_time = cv2.getTickCount() - start_time
        fps = frames_processed / (elapsed_time / cv2.getTickFrequency())
        print(f"FPS: {fps:.2f}")

    # Draw FPS on the frame
    cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show the frame with detections
    cv2.imshow("YOLO Detection", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
