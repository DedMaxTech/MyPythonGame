import threading
import time


def doubler():
    for i in range(10):
        time.sleep(1)
    print('loop ended')

def lol():
    time.sleep(3)
    print('waited 3 secs')

if __name__ == '__main__':
    t = threading.Thread(target=doubler)
    t.start()
    t2 = threading.Thread(target=lol)
    t2.start()