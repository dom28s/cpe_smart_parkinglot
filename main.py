import threading
import multi_plate_test
import multi_top_test

import multi_plate
import multi_top

import multi_variable

# thread_plate = threading.Thread(target=multi_plate.plateProgram)
# thread_top = threading.Thread(target=multi_top.topProgram)

thread_plate = threading.Thread(target=multi_plate_test.plateProgram)
thread_top = threading.Thread(target=multi_top_test.topProgram)

thread_plate.start()
thread_top.start()
thread_plate.join()
thread_top.join()

print("ทั้งสองโปรแกรมรันเสร็จแล้ว")
