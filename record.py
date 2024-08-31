import cv2
import time
from datetime import datetime

# Define start and end times
start_time = "09:00"
end_time = "10:00"

# start_time = "08:10"
# end_time = "10:11"
# Function to check if the current time is within the recording period
def within_recording_time(start_time, end_time):
    current_time = datetime.now().strftime("%H:%M")
    return start_time <= current_time < end_time

# Initialize video capture (0 for webcam, or provide a video file path)
cap = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

# Get the width and height of the video frames
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Wait until the start time
while datetime.now().strftime("%H:%M") != start_time:
    print("Waiting to start recording...")
    time.sleep(1)  # Sleep for 1 second to prevent busy-waiting

# Create a timestamped filename
timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
filename = f'vdoSave/{timestamp}.avi'

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))

print("Recording started...")

# Start recording until the end time
while within_recording_time(start_time, end_time):
    ret, frame = cap.read()
    if ret:
        # Write the frame to the output file
        out.write(frame)
    else:
        break

print("Recording ended...")

# Release everything when done
cap.release()
out.release()
cv2.destroyAllWindows()
