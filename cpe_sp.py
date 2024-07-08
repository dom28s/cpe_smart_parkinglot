from ultralytics import YOLO
import cv2

# Load the YOLOv8n model (lightweight version)
model = YOLO('yolov8n-seg.pt')

# Open video file (replace 'videos/parking_lot_1.mp4' with your video path)
video_path = 'videos/parking_lot_1.mp4'
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error opening video file!")
    exit()

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create video writer for segmented output (replace 'output_segmentation.avi' with your desired output filename)
out = cv2.VideoWriter('output_segmentation.avi', cv2.VideoWriter_fourcc(*'MJPG'), fps, (width, height))

# Process video frames
while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    # Perform segmentation on the current frame
       # Perform segmentation on the current frame
    results = model(frame)

    # Extract detection results
    for detection in results[0].boxes:  # Access boxes directly

        # Check for complete detection information (at least 6 elements)
        if len(detection) < 6:
            continue  # Skip to the next detection if incomplete

        class_id, confidence, x_min, y_min, x_max, y_max = detection.xyxy.tolist()  # Unpack only if valid

        label = model.names[int(class_id)]
        cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
        cv2.putText(frame, f'{label} {confidence:.2f}', (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


    # Write segmented frame to the output video
    out.write(frame)

    # Display the segmented frame
    cv2.imshow('Segmentation', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print("Segmentation complete. Output video saved as 'output_segmentation.avi'.")
