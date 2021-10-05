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
    font = pg.font.SysFont('Arial',size=20)
    screen.blit(font.render(str(var), True, 'red'), (x, y))

def glow(img:pg.Surface):
    size = img.get_size()[0]*2, img.get_size()[1]*2
    print(img.get_size(),size)
    glowed = pg.transform.scale(img.copy(), size)
    glowed.set_alpha(128)
    sf = pg.Surface(size)

    sf.blit(glowed, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
    sf.blit(img, (size[0] / 2 - img.get_size()[0], size[1] / 2 - img.get_size()[1],))
    return sf


def glitch(surface:pg.Surface, offset:int, rng:int):
    surf = pg.Surface((surface.get_size()[0]+rng, surface.get_size()[1]))
    pa = pg.PixelArray(surf.copy())
    w,h = surface.get_size()
    for y in range(h):
        x = (y+offset) % rng
        print(x,y, pa.shape, surface.get_size())
        pa[x:x+w, y] = pa[0:w, y]
    return pa.make_surface()


@threaded(daemon=False)
def timer(t):
    time.sleep(t)
    print(t)

