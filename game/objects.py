from . import core
from . utils import *

def create_portals(pos1, pos2, size = (40,40)):
    p1 = Portal(pos1,size)
    p2 = Portal(pos2, size)
    p1.second, p2.second = p2,p1
    return p1,p2


PORTAL_IMG = pg.image.load('game/content/portal.png')
sounds = not pg.mixer.get_init() is None
print('sound',sounds)
if sounds:
    sound = pg.mixer.Sound('game/content/sounds/portal.wav')
    sound.set_volume(0.2)
class Portal(core.Actor):
    def __init__(self, pos,size = (40,40), second = None):
        x,y = pos; w,h = size
        super().__init__(x, y, w,h, static=True)
        self.second = second
        self.ignore = []
        self.img = pg.transform.scale(PORTAL_IMG.copy(), size)
        self.r = 0
    def update(self, delta, blocks, actors):
        self.r += 10
        self.r = self.r%360
        self.img = pg.transform.rotate(PORTAL_IMG.copy(),self.r//90)
        self.img = pg.transform.scale(self.img, (self.rect.w,self.rect.h))
        for i in self.ignore:
            i[0] -= delta
            if i[0] <=0:
                del self.ignore[self.ignore.index(i)]
        self._collide_actors(actors)
        self.pre_rect.center = self.rect.center
    def hit(self, actor):
        ignore = [a for kd, a in self.ignore]
        if isinstance(actor, core.Actor) and self.second and actor not in ignore:
            x,y = real(actor.rect.topleft, self.rect)
            self.second.ignore.append([500,actor])
            actor.rect.y = self.second.rect.y+y
            actor.rect.centerx = self.second.rect.centerx

            actor.yspeed = -actor.yspeed
            # actor.xspeed = -actor.xspeed
            if sounds: sound.play()