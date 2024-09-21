import threading
import test2
import test1
# สร้าง thread สำหรับฟังก์ชันแต่ละตัว
thread1 = threading.Thread(target=test1.print_numbers)
thread2 = threading.Thread(target=test2.print_letters)

# เริ่ม thread ทั้งสอง
thread1.start()
thread2.start()

# รอให้ thread ทั้งสองทำงานเสร็จ
thread1.join()
thread2.join()

print("ทั้งสองฟังก์ชันทำงานเสร็จแล้ว")
