import pygame as pg
from game import core
import cfg

class BloodParticle(core.Actor):
    def __init__(self, x, y, w, xv,yv):
        super().__init__(x, y, w, w,friction=0,collision=False)
        self.xspeed, self.yspeed = xv,yv
        self.autodel(1)

class DamageParticle(core.Actor):
    def __init__(self, x, y, dmg,w,  xv,yv):
        super().__init__(x, y, w, w, gravity=0.2,friction=0,collision=False)
        self.xspeed, self.yspeed = xv,yv
        # self.autodel(2)
        self.text = f'{dmg}hp'
        # self.font = 
    
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        screen.blit(pg.font.Font(cfg.font, self.rect.w).render(self.text,False,'red'), (self.rect.x - camera.x, self.rect.y - camera.y,))
        self.rect.w-=0.5
        if self.rect.w<=0: self.delete()
