import time, math
import threading, pickle
from typing import Tuple, Union
import pygame as pg


def threaded(daemon=True):
    def decor(func):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
            t.start()
        return wrapper
    return decor

font = pg.font.SysFont('Arial',size=14)
def debug(var, screen:pg.Surface, x=0, y=0):
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

def distanse(pos1, pos2):
    x,y = abs(pos1[0]-pos2[0]), abs(pos1[1]-pos2[1])
    return (x*x+y*y)**0.5

def angle(pos1,pos2=(0,0)):
    x,y = pos1[0] - pos2[0], pos2[1]-pos1[1]
    if x == 0: x = 0.0001
    return math.degrees(math.atan(y/x))

def vec_to_speed(vec, angle):
    xvel = vec * math.cos(math.radians(angle))
    yvel = vec * math.sin(math.radians(angle))
    return xvel, yvel

def vec_sum(vec1,vec2):
    return (vec1[0]+vec2[0],vec1[1]+vec2[1],)

def real(pos:Union[Tuple[int,int], pg.Rect], camera:pg.Rect):
    if type(pos)==pg.Rect:
        return pg.Rect(pos.x - camera.x, pos.y - camera.y,pos.w, pos.h)
    else:
        return pos[0] - camera.x, pos[1] - camera.y

def get_stat(key=None):
    d= dict()
    try:
        d = pickle.load(open('stats.p', 'rb'))
    except EOFError:
        d = dict()
    # with open('stats.p', 'rb') as file:
    #     d = dict() if not file.readlines() else pickle.load(file)
    #     print(d)
    return d if key is None else d.get(key)

def write_stat(key, val):
    d = get_stat()
    d[key] = val
    with open('stats.p','wb') as file:
        pickle.dump(d,file)

def remap(val, in_boubds:Tuple[float,float], out_bounds:Tuple[float,float]=(0,1)):
    return (val - in_boubds[0]) * (out_bounds[1] - out_bounds[0]) / (in_boubds[1] - in_boubds[0]) + out_bounds[0]

remap(50, (0,100), (500,1280))
@threaded(daemon=False)
def timer(t):
    time.sleep(t)
    print(t)
