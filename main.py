import threading
import multi_plate_test
import multi_top_test
import multi_variable
import multi_plate
import multi_top
import cv2 as cv

# ตัวแปรสำหรับหยุดเธรด
multi_variable.stop_threads = False

def main():
    thread_plate = threading.Thread(target=multi_plate_test.plateProgram)
    thread_top = threading.Thread(target=multi_top_test.topProgram)

    # thread_plate = threading.Thread(target=multi_plate.plateProgram)
    # thread_top = threading.Thread(target=multi_top.topProgram)
    
    thread_plate.start()
    thread_top.start()

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            print("หยุดโปรแกรม...")
            multi_variable.stop_threads = True  # ตั้งค่า flag เพื่อหยุดเธรด
            break

    # รอให้เธรดทำงานเสร็จ
    thread_plate.join()
    thread_top.join()

    print("ทั้งสองโปรแกรมรันเสร็จแล้ว")

if __name__ == "__main__":
    main()
