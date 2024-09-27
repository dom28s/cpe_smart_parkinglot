import threading
import multi_plate_test
import multi_top_test
import multi_variable
import cv2 as cv
import time
from flask import Flask, Response, render_template
import test2

# ตัวแปรสำหรับหยุดเธรด
multi_variable.stop_threads = False

app = Flask(__name__)

# Route to stream video frames
@app.route('/video_feed')
def video_feed():
    return Response(multi_top_test.generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Home route
@app.route('/')
def home():
    return """
    <h1>Video Stream</h1>
    <img src="/video_feed" width="1000">
    """

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    # Start the Flask server in a new thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    thread_plate = threading.Thread(target=multi_plate_test.plateProgram)
    thread_top = threading.Thread(target=multi_top_test.topProgram)

    thread_plate.start()
    time.sleep(1)
    print('ddd')
    thread_top.start()

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            print("หยุดโปรแกรม...")
            multi_variable.stop_threads = True  # ตั้งค่า flag เพื่อหยุดเธรด
            break

    # รอให้เธรดทำงานเสร็จ
    thread_plate.join()
    thread_top.join()
    flask_thread.join()

    print("ทั้งสองโปรแกรมรันเสร็จแล้ว")

if __name__ == "__main__":
    main()
