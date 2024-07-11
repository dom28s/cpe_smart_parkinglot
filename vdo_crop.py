from ultralytics import YOLO
import cv2 as cv
import threading
import queue
import time

# Load YOLO models
LModel = YOLO('model/licenplate.pt') # Sending model to GPU
NModel = YOLO('model/number.pt')  # Sending model to GPU

# Queue for storing frames with limited size
frame_queue = queue.Queue(maxsize=10)
processed_frame_queue = queue.Queue(maxsize=10)

# Function to read frames from video, reading every 2nd frame
def read_frames(video_path):
    vdo = cv.VideoCapture(video_path)
    frame_count = 0
    while True:
        ret, frame = vdo.read()
        if not ret:
            frame_queue.put(None)  # Signal that video reading is done
            break
        
        frame_count += 1
        if frame_count % 3 == 0:  # Read every 2nd frame
            frame_resized = cv.resize(frame, (640, 480))  # Adjust size as needed
            frame_queue.put(frame_resized)
            if frame_queue.full():
                frame_queue.join()

    vdo.release()

# Function to process frames
def process_frames():
    while True:
        frame = frame_queue.get()
        if frame is None:
            processed_frame_queue.put(None)
            frame_queue.task_done()
            break
        
        start_time = time.time()

        # Process frame with license plate model (LModel)
        Lresult = LModel(frame, conf=0.6, iou=0.4)

        for x in Lresult[0].boxes:
            name = Lresult[0].names[int(x.cls)]
            pix = x.xyxy[0].tolist()

            cv.putText(frame, "%s %.2f" % (str(name), (float(x.conf))), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv.rectangle(frame, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)

            # Crop and process the region containing the number plate
            cropped_pic = frame[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
            if cropped_pic.size != 0:  # Ensure the cropped image is not empty
                Nresult = NModel(cropped_pic, conf=0.6, iou=0.4)
                for i in Nresult[0].boxes:
                    Nname = Nresult[0].names[int(i.cls)]
                    Npix = i.xyxy[0].tolist()

                    cv.putText(cropped_pic, "%s" % str(Nname), (int(Npix[0]), int(Npix[1])), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    cv.rectangle(cropped_pic, (int(Npix[0]), int(Npix[1])), (int(Npix[2]), int(Npix[3])), (0, 255, 0), 1)

        end_time = time.time()
        print(f"Frame processed in {end_time - start_time:.4f} seconds")

        processed_frame_queue.put(frame)
        frame_queue.task_done()

# Function to display frames
def display_frames():
    while True:
        frame = processed_frame_queue.get()
        if frame is None:
            processed_frame_queue.task_done()
            break

        cv.imshow('Annotated Image', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        processed_frame_queue.task_done()

    cv.destroyAllWindows()

# Main script execution
if __name__ == "__main__":
    video_path = 'videos/licen_vdo.mp4'
    
    read_thread = threading.Thread(target=read_frames, args=(video_path,))
    process_thread = threading.Thread(target=process_frames)
    display_thread = threading.Thread(target=display_frames)

    read_thread.start()
    process_thread.start()
    display_thread.start()

    read_thread.join()
    process_thread.join()
    processed_frame_queue.put(None)  # Signal the display thread to exit
    display_thread.join()
