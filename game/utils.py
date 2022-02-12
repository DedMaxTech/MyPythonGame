import time, math
import threading, pickle
from typing import *
import pygame as pg


# tasks = []

# def new_task(func, time,loop=False):
#     tasks.append([func,time,loop])

def threaded(daemon=True):
    """Function, wrapped in this decorator, 'll be launched in new thread

    Args:
        daemon (bool, optional): If False, script wait for thread end. Defaults to True.
    """

    def decor(func):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
            t.start()

        return wrapper

    return decor


class Vec(pg.math.Vector2):
    """Creates 2D vector that you can +,-,*,/, lenth, angle, ect...
    """
    def angle(self) -> float:
        """Get vector angle from -180 to 180
        Returns:
            float: Angle  in range +- 180
        """
        a = math.degrees(math.acos(self.x / self.length()))
        return a if self.y > 0 else -a

font = pg.font.SysFont('Arial', size=14)


def debug(var:Any, screen: pg.Surface, x=0, y=0):
    """Draw any value on screen
    Args:
        var (Any): Any value
        screen (pg.Surface): Where to draw
        x (int, optional): Coord X. Defaults to 0.
        y (int, optional): Coord Y. Defaults to 0.
    """
    screen.blit(font.render(str(var), True, 'red'), (x, y))


def distanse(pos1: Tuple[int,int], pos2:Tuple[int,int]) -> float:
    """Distance for 2 objects
    Args:
        pos1 (Tuple[int,int] or pg.Rect): Rect obj or coordinates
        pos2 (Tuple[int,int] or pg.Rect): Rect obj or coordinates
    Returns:
        float: distanse
    """
    if isinstance(pos1, pg.Rect): pos1=pos1.center
    if isinstance(pos2, pg.Rect): pos2=pos2.center
    x, y = abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1])
    return (x * x + y * y) ** 0.5


def angle(pos1:Tuple[int, int], pos2:Tuple[int, int]=(0, 0)):
    """Angle to point, defoult coordinate center is 0,0
    Args:
        pos1 (Tuple[int, int]): Point for angle
        pos2 (Tuple[int, int], optional): Coordinate center. Defaults to (0, 0).
    Returns:
        float: Angle
    """
    x, y = pos1[0] - pos2[0], pos2[1] - pos1[1]
    l = (x * x + y * y) ** 0.5
    if not l: return 0
    a = math.degrees(math.acos(x / l))
    return a if y > 0 else -a


def vec_to_speed(vec:float, angle:float) -> Tuple[float, float]:
    return vec * math.cos(math.radians(angle)), vec * math.sin(math.radians(angle))


def vec_sum(vec1:Tuple[float, float], vec2:Tuple[float, float]) -> Tuple[float, float]:
    """coordinates sum
    Args:
        vec1 (Tuple[float, float]): 1st point
        vec2 (Tuple[float, float]): 2nd point
    Returns:
        Tuple[float, float]: Sum
    """
    return vec1[0] + vec2[0], vec1[1] + vec2[1]


def vec_delta(vec1:Tuple[float, float], vec2:Tuple[float, float]) -> Tuple[float, float]:
    """coordinates delta

    Args:
        vec1 (Tuple[float, float]): 1st point
        vec2 (Tuple[float, float]): 2nd point

    Returns:
        Tuple[float, float]: Delta
    """
    return vec1[0] - vec2[0], vec1[1] - vec2[1]


def real(pos: Union[Tuple[int, int], pg.Rect], camera: pg.Rect, invert=False) -> Tuple[int, int]:
    """Transfer coordinates to camera

    Args:
        pos (Union[Tuple[int, int], pg.Rect]): Point or Rect
        camera (pg.Rect): Camera rect
        invert (bool, optional): Invert for some cases. Defaults to False.

    Returns:
        Tuple[int, int]: Coords
    """
    if not invert:
        if type(pos) == pg.Rect:
            return pg.Rect(pos.x - camera.x, pos.y - camera.y, pos.w, pos.h)
        else:
            return pos[0] - camera.x, pos[1] - camera.y
    else:
        if type(pos) == pg.Rect:
            return pg.Rect(pos.x + camera.x, pos.y + camera.y, pos.w, pos.h)
        else:
            return pos[0] + camera.x, pos[1] + camera.y


def offset_rotation(img:pg.Surface, angle, offset=(0,0),pos=(0,0)):
    offset = pg.Vector2(img.get_width()/2-offset[0],img.get_height()/2-offset[1])
    img = pg.transform.rotate(img, -angle)
    off = offset.rotate(angle)
    pos = off.xy + (pos[0]-(img.get_width()/2),pos[1]-(img.get_height()/2))
    return img, pos


def limit(val: float, min:float=None, max:float =None) -> float:
    """Return value in min&max bounds

    Returns:
        float: val in bounds
    """
    if min is not None and min > val: return min
    elif max is not None and val > max: return max
    else: return val


def get_stat(key=None):
    d = dict()
    try:
        d = pickle.load(open('stats.p', 'rb'))
    except EOFError:
        d = dict()
    return d if key is None else d.get(key)


def write_stat(key, val):
    d = get_stat()
    d[key] = val
    with open('stats.p', 'wb') as file:
        pickle.dump(d, file)


def write_stats(d):
    with open('stats.p', 'wb') as file:
        pickle.dump(d, file)


def remap(val: float, in_boubds: Tuple[float, float], out_bounds: Tuple[float, float] = (0, 1)) -> float:
    return (val - in_boubds[0]) * (out_bounds[1] - out_bounds[0]) / (in_boubds[1] - in_boubds[0]) + out_bounds[0]


@threaded(daemon=False)
def timer(t):
    time.sleep(t)
    print(t)
class Status:
    Offline='f'
    Host='h'
    Listen='l'
