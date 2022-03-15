import pygame as pg
from . import core, enemies,player, fx,level
from .utils import *
import cfg
from random import randint as rd

sounds = not pg.mixer.get_init() is None
if sounds:
    SOUNDS = {
        'jump':pg.mixer.Sound('game/content/sounds/jump.wav'),
        'hurt':pg.mixer.Sound('game/content/sounds/hurt.wav'),
        'shoot':pg.mixer.Sound('game/content/sounds/shoot.wav'),
        'expl':pg.mixer.Sound('game/content/sounds/explosion.wav'),
    }

class Projectile(core.Actor):
    def __init__(self, x, y, xv,yv, img, rot, dmg, parent, bounce=0, gravity=0.1, friction=0):
        w,h = img.get_size()
        super().__init__(x, y, w, h, bounce, gravity,friction=friction)
        self.autodel(20)
        self.parent = parent
        self.damage = dmg
        self.img_orig = img
        self.img = pg.transform.rotate(img, abs(rot)).convert_alpha()
        self.speed.xy = xv,yv
        if xv < 0:
            self.img = pg.transform.flip(self.img,True,False)
        if yv > 0:
            self.img = pg.transform.flip(self.img,False,True)
        self.ignore_tmr = 200
        self.pre_rect = pg.Rect(x-50,y-50,w+50,h+50)
        self.rot_tick = 20000
        self.rot_timer = self.rot_tick

    def update(self, delta, blocks, actors):
        if self.ignore_tmr>0: self.ignore_tmr-=delta
        if self.rot_timer>0: self.rot_timer-=delta
        else:
            self.img = pg.transform.rotate(self.img_orig.copy(), angle(self.speed.xy))
            self.rot_timer = 200
        return super().update(delta, blocks, actors)


    def reset(self):
        self.img = pg.transform.flip(self.img,False,True)

class Bullet(Projectile):
    def hit(self, actor):
        if actor == self.parent and self.ignore_tmr>0:
            return
        if isinstance(actor, enemies.BaseAI) and not isinstance(self.parent, enemies.BaseAI):
            actor.hp -= self.damage
            self.parent.game.stats['done damage']+=self.damage
            self.parent.score += self.damage
            if actor.hp<0: self.parent.score += 100
            self.parent.score_t += self.damage
            if actor.hp<0: self.parent.score_t += 100
            # write_stat('done damage', get_stat('done damage')+self.damage)
            if not cfg.potato:
                fx.blood(self.rect.center,self.parent.world, int(self.damage*1.5/10))
                fx.damage(self.rect.center,self.damage,self.parent.world)
            if sounds: SOUNDS['hurt'].play()
            if self.parent.aim_time < self.parent.AIM_TIME_MAX: self.parent.aim_time+=self.damage*10
            self._delete = True
        if isinstance(actor, player.Player):
            actor.damage(self.damage)
            self.parent.game.stats['received damage']+=self.damage
            # write_stat('received damage', get_stat('received damage')+self.damage)
            actor.dmg_timer = 100
            self._delete = True
        if isinstance(actor, level.Block):
            if actor.type in [i for i in level.block_s if level.block_s[i]['dest']]: 
                # actor.set_type('0')
                actor.delete()
            self.delete()

class Rocket(Projectile):
    def __init__(self, x, y, xv, yv, img, rot, dmg, parent):
        super().__init__(x, y, xv, yv, img, rot, dmg, parent, 0, 0.3, 0)
        self.rot_tick = 200
        self.rot_timer = self.rot_tick
    
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        fx.fire(self.rect.center, self.parent.game.world,2)
        return super().draw(screen, camera)
    
    def hit(self, actor):
        if self.parent == actor and self.ignore_tmr>0:return
        if type(actor) in [player.Player,level.Block] or isinstance(actor, enemies.BaseAI):
            r = 230
            dest = [key for key, val in level.block_s.items() if val['dest']]
            for a in self.parent.game.world.actors+self.parent.game.world.blocks:
                if isinstance(a, core.Actor):
                    d = distanse(self.rect.center, a.rect.center)
                    if d<r:
                        dmg=int(remap(r-d, (0,r), (20,99)))
                        xv,yv = vec_to_speed(dmg/5, 180-angle(a.rect.center,self.rect.center,))
                        # a.speed.xy = xv if self.rect.x>a.rect.x else -xv,(yv if self.rect.x>a.rect.x else -yv)-1
                        a.speed.xy = -xv, -yv
                        a.on_fire = rd(5000,8000)
                        if isinstance(a, player.Player) or isinstance(a, enemies.BaseAI):
                            self.parent.game.stats['done damage']+=dmg
                            if isinstance(a, player.Player): 
                                a.damage(dmg)
                                self.parent.game.stats['done damage']+=self.damage
                                self.parent.score += self.damage
                                if actor.hp<0: self.parent.score += 100
                                self.parent.score_t += self.damage
                                if actor.hp<0: self.parent.score_t += 100
                            else: a.hp-=dmg
                            if not cfg.potato: fx.damage(a.rect.center, dmg, self.parent.game.world)
                if isinstance(a, level.Block) and a.type in dest:
                    a.delete()
            self.parent.game.shake=20
            if sounds: SOUNDS['expl'].play()
            if not cfg.potato: fx.explosion(self.rect.center,self.parent.game.world, 30)
            self.delete()

# class Gun:
#     def __init__(self, img,pos=(29,29),offx=0,offy=0,bull_pos=(0,0),mag=10,) -> None:
#         pass

GUNS = {
    'rifle': {'img': pg.image.load('game/content/player/guns/rifle.png'),
              'pos': (29, 29),
              'offx':0,
              'offy':0,
              'bull_pos': (0, 0),
              'bullet':Bullet,
              'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
              'speed': 20,
              'mag': 30,
              'amount': 1,
              'reload':1500,
              'dmg':15,
              'kd':100,
              'acc':2,
              'auto': True,
              'shake':7,
              'back':1,
              'recoil':10},
    'pistol': {'img': pg.image.load('game/content/player2/guns/pistol.png'),
               'pos': (29, 29),
               'offx':0,
               'offy':0,
               'bull_pos': (0, 0),
              'bullet':Bullet,
               'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
               'speed': 25,
               'mag': 10,
               'amount': 1,
               'reload': 1000,
               'dmg':35,
               'kd':300,
               'acc':1,
               'auto': False,
               'shake':9,
               'back':3,
               'recoil':50},
    'shootgun': {'img': pg.image.load('game/content/player2/guns/shootgun.png'),
            'pos': (29, 29),
            'offx':0,
            'offy':-2,
            'bull_pos': (0, 0),
              'bullet':Bullet,
            'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
            'speed': 25,
            'mag': 5,
            'amount': 5,
            'reload': 3000,
            'dmg':15,
            'kd':350,
            'acc':2,
            'auto': False,
            'shake':15,
            'back':10,
            'recoil':70},
    'minigun': {'img': pg.image.load('game/content/player2/guns/minigun.png'),
            'pos': (29, 29),
            'offx':0,
            'offy':-5,
            'bull_pos': (0, 0),
              'bullet':Bullet,
            'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
            'speed': 25,
            'mag': 100,
            'amount': 1,
            'reload': 3000,
            'dmg':7,
            'kd':50,
            'acc':1,
            'auto': True,
            'shake':5,
            'back':1,
            'recoil':4},
    'sniper': {'img': pg.image.load('game/content/player2/guns/sniper.png'),
            'pos': (29, 29),
            'offx':7,
            'offy':-5,
            'bull_pos': (0, 0),
            'bullet':Bullet,
            'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
            'speed': 30,
            'mag': 5,
            'amount': 1,
            'reload': 2000,
            'dmg':130,
            'kd':600,
            'acc':1,
            'auto': False,
            'shake':20,
            'back':7,
            'recoil':90},
    'rocket_gun': {
        'img': pg.image.load('game/content/player2/guns/rocket_gun.png'),
        'pos': (29, 29),
        'offx':0,
        'offy':0,
        'bull_pos': (0, 0),
        'bullet':Rocket,
        'bull_img':pg.image.load('game/content/player2/guns/rocket.png'),
        'speed': 15,
        'mag': 1,
        'amount': 1,
        'reload': 1500,
        'dmg':130,
        'kd':600,
        'acc':1,
        'auto': False,
        'shake':20,
        'back':7,
        'recoil':90},
}
