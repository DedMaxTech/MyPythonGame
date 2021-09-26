import time
import threading


def threaded(daemon=True):
    def decor(func):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
            t.start()

        return wrapper

    return decor

