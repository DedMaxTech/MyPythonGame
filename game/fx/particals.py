import pygame as pg
from game import core
import cfg
from random import randint as rd

from game.utils import *

class BloodParticle(core.Actor):
    def __init__(self, x, y, w, xv,yv):
        super().__init__(x, y, w, w,friction=0,collision=False)
        self.speed = Vec(xv,yv)
        self.autodel(1)

class DamageParticle(core.Actor):
    def __init__(self, x, y, dmg,w,  xv,yv, heal=False):
        super().__init__(x, y, w, w, gravity=0.2,friction=0,collision=False)
        self.speed = Vec(xv,yv)
        # self.autodel(2)
        self.text = f'+{dmg}hp' if heal else f'-{dmg}hp' 
        # self.font =   
        self.heal = heal
        self.rect.w=int((w**0.5)*5)
        self.font=pg.font.Font(cfg.font, self.rect.w)
        self.autodel(3)
    
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        screen.blit(self.font.render(self.text,False,'red' if not self.heal else 'green'), (self.rect.x - camera.x, self.rect.y - camera.y,))
        self.rect.w-=0.5
        # if self.rect.w<=0: self.delete()

class ExploseParticle(core.Actor):
    def __init__(self, x, y, w):
        super().__init__(x, y, w,1,gravity=0, static=True, friction=0, collision=False)
        sf = pg.Surface((w*2,w*2))
        self.w=1
        pg.draw.circle(sf, (255, rd(0,200), 0), (w,w),w)
        self.img = sf
        self.img.set_colorkey('black')
        self.side = rd(1,5)

    def update(self, delta, blocks, actors):
        self.w*=1.2
        w = self.rect.w
        if self.w>w*2: self.delete()
        coord=(w,w)
        if self.side==1: coord = (0,0)
        if self.side==2: coord = (0,w)
        if self.side==3: coord = (w,0)
        if self.side==4: coord = (w,w)
        pg.draw.circle(self.img, 'black', coord, self.w,)
    
    def light_draw(self, screen: pg.Surface, camera: pg.Rect):
        screen.blit(self.img, real(self.rect.topleft, camera))
