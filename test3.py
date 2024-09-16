import threading
import test1
import test2


thread1 = threading.Thread(target=test1.loop1)
thread2 = threading.Thread(target=test2.loop2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("ทั้งสองโปรแกรมรันเสร็จแล้ว")
