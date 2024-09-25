from flask import Flask, Response
import cv2

# Create a Flask app
app = Flask(__name__)

# Open the video stream from the RTSP URL
cap = cv2.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

def generate_frames():
    while True:
        # Read a frame from the video stream
        success, frame = cap.read()
        if not success:
            break  # Exit loop if reading the frame fails

        # Encode the frame as JPEG
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue  # Skip to the next iteration if encoding fails

        # Convert the buffer to bytes
        frame_bytes = buffer.tobytes()
        
        # Yield the frame in the correct format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Create a streaming response for the video feed
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Render the HTML page to display the video stream
    return '''
        <html>
            <body>
                <h1>Video Feed</h1>
                <img src="/video_feed">  <!-- This will display the video stream -->
            </body>
        </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)  # Start the Flask app in debug mode
