from typing import List
from pygame import event
from . import core, player
from . utils import *

def create_portals(pos1, pos2, size = (40,40)):
    p1 = Portal(pos1,size)
    p2 = Portal(pos2, size)
    p1.second, p2.second = p2,p1
    return [p1,p2]


PORTAL_IMG = pg.image.load('game/content/portal2.png')
sounds = not pg.mixer.get_init() is None
if sounds:
    sound = pg.mixer.Sound('game/content/sounds/portal.wav')
    sound.set_volume(0.2)
class Portal(core.Actor):
    def __init__(self, pos,size = (40,40), second = None):
        global PORTAL_IMG
        x,y = pos; w,h = size
        super().__init__(x, y, w,h, static=True)
        self.second = second
        self.ignore = []
        PORTAL_IMG = PORTAL_IMG.convert_alpha()
        self.img = pg.transform.scale(PORTAL_IMG.copy(), size)
        self.r = 0
    def update(self, delta, blocks, actors):
        self.r += 1
        # self.r = self.r%360
        self.img = pg.transform.rotate(PORTAL_IMG.copy(),self.r)
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

class BaseTriger(core.Actor):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, bounce=0, gravity=0, static=False, friction=0, collision=True)
        self.game = None
        self.visible = False

    def hit(self, actor):
        if type(actor) == player.Player and self.game:
            self.triggered(actor)
    def triggered(self, actor):
        pass


def create_zoom_zone(x,y,w,h,zoom, defoult=1):
    return Trigger(x,y,20,h, lambda game: game.zoom(defoult)),Trigger(x+20,y,20,h, lambda game: game.zoom(zoom)),Trigger(x+w,y,20,h, lambda game: game.zoom(zoom)),Trigger(x+w+20,y,20,h, lambda game: game.zoom(defoult)),
class Trigger(BaseTriger):
    def __init__(self, x, y, w, h, func):
        super().__init__(x, y, w, h)
        self.func = func
    
    def triggered(self, actor):
        self.func(self.game)

class Aid(BaseTriger):
    def __init__(self, x, y, hp):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity=0.4
        self.img = pg.image.load('game/content/objects/aid.png').convert_alpha()
        self.hp = hp
    
    def triggered(self, actor):
        if actor.hp+self.hp>actor.max_hp: actor.hp = actor.max_hp
        else: actor.hp+=self.hp
        self.delete()

class Ammo(BaseTriger):
    def __init__(self, x, y, ammo:dict):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity=0.4
        self.img = pg.transform.scale(pg.image.load('game/content/ui/ammo.png'),(25,25)).convert_alpha()
        self.ammo = ammo
    
    def triggered(self, actor):
        for key, val in self.ammo.items():
            if actor.ammo.get(key):actor.ammo[key][1]+=val
            else: actor.ammo[key] = [0, val]
        self.delete()

class GunsCase(BaseTriger):
    def __init__(self, x, y, guns:List[str]):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity=0.4
        self.img = pg.image.load('game/content/objects/guns.png').convert_alpha()
        self.guns = guns
    
    def triggered(self, actor):
        actor.guns = list(set(actor.guns+self.guns))
        self.delete()

class ScreenTriger(BaseTriger):
    BASE_IMG = pg.image.load('game/content/ui/trigger_base.png')
    def __init__(self, x, y, w, h, image, timer=3000):
        super().__init__(x, y, w, h)
        self.image = pg.image.load(image)
        # self.visible=True
        self.timer = timer
    
    def update(self, delta, blocks, actors):
        if self.visible and self.timer >0: self.timer-=delta
        if self.timer<=0: self.delete()
        self._collide_actors(actors)

    def triggered(self, actor):
        self.visible=True
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        if self.visible: self.game.screen.blit(self.image, (0,0))

class LevelTravelTriger(BaseTriger):
    def __init__(self, x, y, w, h, levelname):
        super().__init__(x, y, w, h)
        self.visible=True
        self.img = pg.transform.scale(PORTAL_IMG.copy(), (w,h))
        self.level = levelname
        self.r=0
    
    def update(self, delta, blocks, actors):
        self.r+=1
        self.img = pg.transform.rotate(PORTAL_IMG.copy(),self.r)
        self.img = pg.transform.scale(self.img, (self.rect.w,self.rect.h))
        return super().update(delta, blocks, actors)
    
    def triggered(self, actor):
        self.game.start_game(self.level)

class ScreenConditionTriger(BaseTriger):
    def __init__(self, x, y, w, h, image,condition):
        super().__init__(x, y, w, h)
        self.image = pg.image.load(image).convert_alpha()
        self.condition = condition
        self.ok = False
        self.OK_IMG = pg.image.load('game/content/ui/screen_ok.png').convert_alpha()
        # self.visible=True
        self.timer = 1000
    
    def update(self, delta, blocks, actors):
        if self.ok and self.timer >0: self.timer-=delta
        if self.visible and self.condition(self.game):
            self.ok=True
        if self.timer<=0: self.delete()
        self._collide_actors(actors)

    def triggered(self, actor):
        self.visible=True
        if self.ok: return
        
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        if self.visible: 
            if not self.ok:self.game.screen.blit(self.image, (0,0))
            else: self.game.screen.blit(self.OK_IMG, (0,0))
