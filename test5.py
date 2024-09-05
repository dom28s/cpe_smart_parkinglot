import time

i =0

while True:
    time.sleep(1)
    i+=1
    print(i)
    if i%10 ==0:
        i=0