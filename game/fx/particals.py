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


class SlimeParticle(core.Actor):
    def __init__(self, x, y, w, xv,yv):
        super().__init__(x, y, w, w,friction=0,collision=False)
        self.speed = Vec(xv,yv)
        self.color = (0,rd(150,250),0, rd(150,255))
        self.timer = 500
        self.autodel(4)
    
    def update(self, delta, blocks, actors):
        if self.timer>0: self.timer-=delta
        else:
            self.rect.w -=1
            self.rect.h -=1
            self.timer=500
            if self.rect.w ==0:
                self.delete()
        return super().update(delta, blocks, actors)
    
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        screen.fill(self.color, real(self.rect, camera))

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

class Star():
    def __init__(self) -> None:
        self.w = 2.0
        angle = rd(0,3600)/10
        self.pos = pg.Vector2((854/2,480/2)+pg.Vector2(30,0).rotate(angle)) # pg.Rect(rd(854/2-30,854/2+30),rd(480/2-30,480/2+30),w,w)
        self.vec = pg.Vector2(1,0).rotate(angle)
        self._del = False
        self.frames = 0
    def update(self):
        self.frames+=1
        self.w *= 1.04
        self.vec *= 1.05
        self.pos += self.vec
        if not pg.Rect(-200,-200,1000,680).collidepoint(self.pos):self._del = True
        # self.color = pg.Color(rd(0,))
    def draw(self,frame):
        pg.draw.rect(frame,(limit(int(self.frames*2.5),max=255),limit(int(self.frames*2.5),max=255),limit(int(self.frames*2.5),max=255),),(self.pos.x,self.pos.y,self.w,self.w))