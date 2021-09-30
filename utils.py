import time
import threading
import pygame as pg


def threaded(daemon=True):
    def decor(func):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
            t.start()
        return wrapper
    return decor


def debug(var, screen:pg.Surface, x=0, y=0):
    font = pg.font.SysFont('Arial',size=10)
    screen.blit(font.render(var, True, 'red'), (x, y))


@threaded(daemon=False)
def timer(t):
    time.sleep(t)
    print(t)

