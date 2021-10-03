import pygame as pg
from functools import cache
from time import sleep
from game.utils import *

class Actor:
    def __init__(self, x, y, w, h, bounce=0.0, gravity=0.4, static=False, friction=0.995):
        self.rect = pg.Rect(x,y,w,h)
        self.xvel, self.yvel = 0.0,0.0
        self.gravity, self.bounce, self.static, self.friction = gravity, bounce, static, friction
        self.on_ground = False
        self._delete = False
        
        self.autodel()
    
    @threaded()
    def autodel(self):
        sleep(10)
        print('del')
        self._delete = True

    def update(self, delta, blocks):
        if self.static:
            return
        
        self.on_ground = self._check_on_ground(blocks)

        if not self.on_ground:
            self.yvel += self.gravity
            
        else:
            if self.yvel > 2:
                self.yvel = -self.yvel*self.bounce
            else: self.yvel =0
            if abs(self.xvel) > 0.1:
                self.xvel = self.xvel*self.friction
            else: self.xvel =0

        self.rect.y += self.yvel
        self._collide_y(blocks)
        self.rect.x += self.xvel
        self._collide_x(blocks)
    
    def delete(self):
        self._delete = True

    def _check_on_ground(self, blocks):
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
                if self.xvel>0:
                    self.rect.right = b.rect.left
                elif self.xvel < 0:
                    self.rect.left = b.rect.right
                self.hit(b)
                if abs(self.xvel) > 1:
                    self.xvel = -self.xvel*self.bounce
                else: self.xvel =0

    def _collide_y(self, blocks):    
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.yvel > 0:
                    # self.yvel = 0
                    self.rect.bottom = b.rect.top
                if self.yvel < 0:
                    self.yvel = 0
                    self.rect.top = b.rect.bottom
                self.hit(b)
    
    def hit(self, actor):
        pass

