import pygame as pg
from functools import cache
from time import sleep
from game.utils import *
import cfg

class Actor:
    def __init__(self, x, y, w, h, bounce=0.0, gravity=0.4, static=False, friction=0.005):
        self.rect = pg.Rect(x,y,w,h)
        self.pre_rect = pg.Rect(x-30,y-30,w+30,h+30)
        self.xspeed, self.yspeed = 0.0, 0.0
        self.gravity, self.bounce, self.static, self.friction = gravity, bounce, static, friction
        self.on_ground = False
        self._delete = False
        
        self.autodel()
    
    @threaded()
    def autodel(self):
        # sleep(7)
        # self.static = True
        sleep(10)
        self._delete = True

    def update(self, delta, blocks):
        if self.static:
            return
        
        self.on_ground = self.check_on_ground(blocks)

        if not self.on_ground:
            self.yspeed += self.gravity
            
        else:
            if abs(self.xspeed) > 0.1:
                self.xspeed = self.xspeed * (1 - self.friction)
            else: self.xspeed =0

        if self.yspeed: self.rect.y += self.yspeed *delta/1000*cfg.fps
        if blocks: self._collide_y(blocks)
        if self.xspeed: self.rect.x += self.xspeed *delta/1000*cfg.fps
        if blocks: self._collide_x(blocks)
        self.pre_rect.center = self.rect.center
    
    def delete(self):
        self._delete = True

    def check_on_ground(self, blocks):
        self.rect.y += 1
        for b in blocks:
            if self.rect.colliderect(b.rect):
                self.rect.y -= 1
                return True
        self.rect.y -= 1
        return False

    def _collide_x(self, blocks):
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.xspeed>0:
                    self.rect.right = b.rect.left
                elif self.xspeed < 0:
                    self.rect.left = b.rect.right
                self.hit(b)
                if abs(self.xspeed) > 1:
                    self.xspeed = -self.xspeed * self.bounce
                else: self.xspeed =0

    def _collide_y(self, blocks):    
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.yspeed > 0:
                    # self.yvel = 0
                    self.rect.bottom = b.rect.top
                if self.yspeed < 0:
                    self.yspeed = 0
                    self.rect.top = b.rect.bottom
                if abs(self.yspeed) > 2:
                    self.yspeed = -self.yspeed * self.bounce
                else:
                    self.yspeed = 0
                self.hit(b)
    
    def hit(self, actor):
        pass

