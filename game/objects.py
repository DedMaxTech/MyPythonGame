from types import FunctionType
from typing import List
from pygame import event

from game.UI import Button
from . import core, player, fx
from . utils import *
import cfg

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

class Portal(core.Actor, core.Saving):
    slots = {
        'x1':['rect.x', int],
        'y1':['rect.y', int],
        'x2':['second.rect.x', int],
        'y2':['second.rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
    }
    def __init__(self, x1=0,y1=0,x2=40,y2=0,w=40,h=40):
        global PORTAL_IMG
        size=(w,h)
        super().__init__(x1, y1, w,h, static=True)
        self.ignore = []
        PORTAL_IMG = PORTAL_IMG.convert_alpha()
        self.img = pg.transform.scale(PORTAL_IMG.copy(), size)
        self.r = 0

        self.second = core.Actor(x2, y2, w,h, static=True)
        self.second.second=self
        self.second.ignore = []
        self.second.img = pg.transform.scale(PORTAL_IMG.copy(), size)
        self.second.r = 0
        self.second.update = self.nothing
        self.second.hit = self.second_hit
    
    
    def set_game(self, game):
        super().set_game(game)
        self.spawn(self.second)

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

        self.second.img=self.img
        self.second._collide_actors(actors)
        self.second.pre_rect.center = self.second.rect.center
    
    def reset(self):
        self.img = pg.transform.scale(self.img, (self.rect.w,self.rect.h))
        self.second.img=self.img

    def hit(self, actor):
        ignore = [a for kd, a in self.ignore]
        if isinstance(actor, core.Actor) and self.second and actor not in ignore:
            self.ignore.append([500,actor])
            x,y = real(actor.rect.topleft, self.rect)
            actor.rect.y = self.second.rect.y+y
            actor.rect.centerx = self.second.rect.centerx

            actor.yspeed = -actor.yspeed
            actor.reset()
            # actor.xspeed = -actor.xspeed
            if sounds: sound.play()
    
    def second_hit(self,actor):
        ignore = [a for kd, a in self.ignore]
        if isinstance(actor, core.Actor) and actor not in ignore:
            self.ignore.append([500,actor])
            x,y = real(actor.rect.topleft, self.second.rect)
            actor.rect.y = self.rect.y+y
            actor.rect.centerx = self.rect.centerx
            actor.yspeed = -actor.yspeed
            actor.reset()
            if sounds: sound.play()

class Text(core.Actor, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'text':['text', str],
        'size':['size', int],
        'color':['color', str],
    }
    def __init__(self, x=0, y=0, text='Text', size=20, color='white'):
        super().__init__(x, y, 1,1, bounce=0, gravity=0, static=False, friction=0, collision=False)
        self.text=text
        self.size=size
        self.color=color
        self.img=pg.font.Font(cfg.font, size).render(text, False, color)
        self.rect.size = self.img.get_size()
    def update(self, delta, blocks, actors):
        pass
    def reset(self):
        self.img=pg.font.Font(cfg.font, self.size).render(self.text, False,self.color)
        self.rect.size = self.img.get_size()
class Image(core.Actor, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'image':['imgfile', str],
        'rotation':['rot', int],
        'scale':['scale', float],
    }
    def __init__(self, x=0, y=0, image='game/content/ui/arrow.png', rotation=0, scale=1):
        img = pg.image.load(image).convert_alpha()
        w,h = img.get_size()
        w,h = int(w*scale), int(h*scale)
        super().__init__(x, y, w,h, bounce=0, gravity=0, static=False, friction=0, collision=False)
        self.imgfile=image
        self.rot = rotation
        self.scale = scale
        self.img=pg.transform.rotate(pg.transform.scale(img,(w,h)),self.rot)
        self.rect.size = self.img.get_size()
    def update(self, delta, blocks, actors):
        pass
    def reset(self):
        img = pg.image.load(self.imgfile).convert_alpha()
        w,h = img.get_size()
        self.rect.size=int(w*self.scale), int(h*self.scale)
        self.img=pg.transform.rotate(pg.transform.scale(img,(self.rect.w,self.rect.h)),self.rot)
        self.rect.size = self.img.get_size()
class BaseTriger(core.Actor, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
    }
    def __init__(self, x=0, y=0, w=40, h=40):
        super().__init__(x, y, w, h, bounce=0, gravity=0, static=False, friction=0, collision=True)
        self.game = None
        self.visible = False

    def hit(self, actor):
        if type(actor) == player.Player and self.game:
            self.triggered(actor)
    def triggered(self, actor):
        pass

class ZoomTriger(BaseTriger):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
        'zoom':['zoom', float]
    }
    def __init__(self, x=0, y=0, w=40, h=40, zoom=0.5):
        super().__init__(x=x, y=y, w=w, h=h)
        self.zoom=zoom
        self.colliding=False
    
    def update(self, delta, blocks, actors):
        c = self.rect.colliderect(self.game.player.rect)
        if c and not self.colliding:
            self.game.zoom(self.zoom)
        elif not c and self.colliding:
            self.game.zoom(1)
        self.colliding=c

def create_zoom_zone(x,y,w,h,zoom, defoult=1):
    return Trigger(x,y,20,h, lambda game: game.zoom(defoult)),Trigger(x+20,y,20,h, lambda game: game.zoom(zoom)),Trigger(x+w,y,20,h, lambda game: game.zoom(zoom)),Trigger(x+w+20,y,20,h, lambda game: game.zoom(defoult)),
class Trigger(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
        'function':['func', FunctionType]
    }
    def __init__(self, x=0, y=0, w=40, h=40, function='1==1'):
        super().__init__(x, y, w, h)
        self.func = function

    def update(self, delta, blocks, actors):
        self._collide_actors(actors)
    def triggered(self, actor):
        game = self.game
        exec(f'{self.func}')
        self.delete()

class DoubleGunBonus(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'time':['time', int]
    }
    def __init__(self, x=0, y=0, time=5000):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity, self.friction=0.4,0.005
        self.frame_timer = 400
        self.cur_img = 0
        self.imgs = [player.GUNS[i]['img'] for i in player.GUNS]
        self.img = self.imgs[0]
        self.time = time
    
    def update(self, delta, blocks, actors):
        if self.frame_timer>0:self.frame_timer-=delta
        else:
            self.frame_timer = 400
            self.cur_img+=1
            self.cur_img = self.cur_img%len(self.imgs)
            self.img = self.imgs[self.cur_img]
        return super().update(delta, blocks, actors)

    def triggered(self, actor):
        actor.bonus['Double gun']+=self.time
        actor.event_ui.add_ui([Button((0,0),'yellow','Double gun:',20)])
        self.delete()

class Aid(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'hp':['hp', int]
    }
    def __init__(self, x=0, y=0, hp=50):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity, self.friction=0.4,0.005
        self.img = pg.image.load('game/content/objects/aid.png').convert_alpha()
        self.hp = hp
    
    def triggered(self, actor):
        if actor.hp+self.hp>actor.max_hp: actor.hp = actor.max_hp
        else: actor.hp+=self.hp
        fx.damage(actor.rect.center, self.hp, self.game.world, True)
        self.delete()
class Grenades(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'amount':['amount', int]
    }
    def __init__(self, x=0, y=0, amount=10):
        super().__init__(x, y, 9,11)
        self.visible=True
        self.gravity, self.friction=0.4,0.005
        self.img = pg.image.load('game/content/ui/grenade.png').convert_alpha()
        self.amount=amount
    
    def triggered(self, actor):
        actor.grenades+=self.amount
        actor.event_ui.add_ui([Button((0,0), 'white', f'grenades: +{self.amount}', 20, autodel=3*1000)])
        self.delete()
class Ammo(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'ammo':['ammo', dict]
    }
    def __init__(self, x=0, y=0, ammo:dict={}):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity, self.friction=0.4,0.005
        self.img = pg.transform.scale(pg.image.load('game/content/ui/ammo.png'),(25,25)).convert_alpha()
        self.ammo = ammo
    
    def triggered(self, actor):
        for key, val in self.ammo.items():
            if actor.ammo.get(key):actor.ammo[key][1]+=val
            else: actor.ammo[key] = [0, val]
        actor.event_ui.add_ui([Button((0,0), 'white', f'{gun}: +{self.ammo[gun]}', 20, autodel=3*1000+i*300) for i, gun in enumerate(self.ammo)])
        self.delete()

class GunsCase(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'guns':['guns', list]
    }
    def __init__(self, x=0, y=0, guns:List[str]=[]):
        super().__init__(x, y, 25,25)
        self.visible=True
        self.gravity, self.friction=0.4,0.005
        self.img = pg.image.load('game/content/objects/guns.png').convert_alpha()
        self.guns = guns
    
    def triggered(self, actor):
        actor.guns = list(set(actor.guns+self.guns))
        actor.event_ui.add_ui([Button((0,0), 'white', f'+ {val}', 20, autodel=(3+i)*1000) for i, val in enumerate(self.guns)])
        self.delete()

class ScreenTriger(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
        'timer':['timer', int],
        'image':['img_name', str]
    }
    BASE_IMG = pg.image.load('game/content/ui/trigger_base.png')
    def __init__(self, x=0, y=0, w=40, h=40, image='game/content/ui/trigger_base.png', timer=3000):
        super().__init__(x, y, w, h)
        self.img_name=image
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

class LevelTravelTriger(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
        'levelname':['level', str],
    }
    def __init__(self, x=0, y=0, w=40, h=40, levelname='tutorial'):
        super().__init__(x, y, w, h)
        self.visible=True
        self.img = pg.transform.scale(PORTAL_IMG.copy(), (w,h))
        self.level = levelname
        self.r=0
        self.timer=1500
        self.t=False
    
    def update(self, delta, blocks, actors):
        if self.t:
            self.rect.x += self.rect.w*0.02
            self.rect.y += self.rect.h*0.02
            self.rect.w*=0.98
            self.rect.h*=0.98
            if self.timer>0: self.timer-=delta
            else: self.game.start_game(self.level)
        self.r+=1
        self.img = pg.transform.rotate(PORTAL_IMG.copy(),self.r)
        self.img = pg.transform.scale(self.img, (self.rect.w,self.rect.h))
        self._collide_actors(actors)
    
    def triggered(self, actor):
        if self.t:return
        self.game.zoom(3)
        self.game.w=cfg.screen_h
        self.game.v=1
        actor.visible=False
        actor.static=True
        self.t=True

class SpawningPortal(core.Actor):

    def __init__(self, x, y, game):
        w,h = 35+10, 63+10
        super().__init__(x-5, y-5, w,h, 0,0,True,0,False)
        self.img = pg.transform.scale(PORTAL_IMG.copy(), (self.rect.w, self.rect.h))
        self.r=0
        self.timer=3000
        self.size = [w,h]
        self.game = game
        self.game.player.visible, self.game.player.static=False,True
    
    def update(self, delta, blocks, actors):
        

        if self.timer>0: self.timer-=delta
        else:
            self.game.player.visible, self.game.player.static=True,False
            self.delete()
            return
        if self.timer<1200:
            self.size[0]*=0.97
            self.size[1]*=0.97
            self.game.player.visible, self.game.player.static=True,False
        self.r+=1
        self.img = pg.transform.rotate(PORTAL_IMG.copy(),self.r)
        self.img = pg.transform.scale(self.img, (int(self.size[0]),int(self.size[1])))
        self._collide_actors(actors)
    
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        screen.blit(self.img, real((self.rect.centerx-(self.size[0]/2),self.rect.centery-(self.size[1]/2)), camera))
    

class ScreenConditionTriger(BaseTriger, core.Saving):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
        'condition':['condition', FunctionType],
        'image':['img_name', str]
    }
    def __init__(self, x=0, y=0, w=40, h=40, image='game/content/ui/screen_ok.png',condition='1==1'):
        super().__init__(x, y, w, h)
        self.img_name=image
        self.image = pg.image.load(image).convert_alpha()
        self.condition = condition
        self.func = eval(f'lambda game: {condition}')
        self.ok = False
        self.OK_IMG = pg.image.load('game/content/ui/screen_ok.png').convert_alpha()
        # self.visible=True
        self.timer = 1000
    
    def update(self, delta, blocks, actors):
        if self.ok and self.timer >0: self.timer-=delta
        if not self.ok and self.visible and self.func(self.game):
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

class CameraTargetTriger(BaseTriger):
    slots = {
        'x':['rect.x', int],
        'y':['rect.y', int],
        'w':['rect.w', int],
        'h':['rect.h', int],
        'target_x':['target.x', int],
        'target_y':['target.y', int],
        'timer':['timer', int]
    }
    def __init__(self, x=0, y=0, w=40, h=40,target_x=0,target_y=0,timer=0):
        super().__init__(x=x, y=y, w=w, h=h)
        self.timer = timer
        self.onetime = timer>0
        self.target=pg.Rect(target_x,target_y,1,1)
        self.t=False
    
    def update(self, delta, blocks, actors):
        if self.onetime:
            print(self.t)
            if self.t:
                if self.timer>0: self.timer-=delta
                else: 
                    self.game.camera_target = None
                    self.delete()
                    return
        else:
            if self.rect.colliderect(self.game.player.rect): self.game.camera_target = self.target
            else: self.game.camera_target = None
        self._collide_actors(actors)
    
    def triggered(self, actor):
        self.t=True
        self.game.camera_target = self.target
    
    def debug_draw(self, screen, camera):
        super().debug_draw(screen, camera)
        pg.draw.rect(screen,'red',(*real((self.target.x-(854/2),self.target.y-(480/2)), camera),854,480), 2)