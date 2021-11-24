from typing import Dict
import pygame as pg
from time import sleep
from . utils import *
import cfg

def_tick=1/60*1000

class SavingYourAnus:
    slots = {}
    def _get_att_val(self,text):
        vals = text.split('.')
        if len(vals)==1: return getattr(self,text)
        last=getattr(self, vals[0])
        for i in text.split('.')[1:]:
            last = getattr(last, i)
        return last
    
    def _set_att_val(self, att, val):
        atts = att.split('.')
        if len(atts)==1: setattr(self, att, val)
        setattr(self._get_att_val('.'.join(atts[:-1])), atts[-1], val)

    def edit(self, attr, val):
        self._set_att_val(self.slots[attr][0],self.slots[attr][1](val))

    def save(self):
        return f'objects.{self.__class__.__name__}({", ".join(["{key}={val}".format(key=key, val=self._get_att_val(val[0])) for key,val in self.slots.items()])})'

class Actor:
    def __init__(self, x, y, w, h, bounce=0.0, gravity=0.4, static=False, friction=0.005, collision=True, image=None):
        self.rect = pg.Rect(x,y,w,h)
        self.pre_rect = pg.Rect(x-30,y-30,w+30,h+30)
        self.xspeed, self.yspeed = 0.0, 0.0
        self.gravity, self.bounce, self.static, self.friction, self.collision = gravity, bounce, static, friction, collision
        self.on_ground = False
        self.need_sides = False
        self.right, self.left = False,False
        self._delete = False
        self.die = False
        self.die_kd = 0
        self.img = image
        self.visible = True
        self.game=None
        # self.autodel()
    
    def autodel(self, secs):
        self.die = True
        self.die_kd = secs*1000
    
    def set_game(self, game):
        self.game=game
    
    def spawn(self, actor):
        if self.game:
            self.game.world.actors.append(actor)

    def update(self, delta, blocks, actors):
        if self.static:
            return
        if self.collision:
            self.on_ground = self.check_on_ground(blocks)
            if self.need_sides: self.right, self.left = self.check_right(blocks), self.check_left(blocks)

        k=delta/def_tick
        # print(k)
        if self.die:
            if self.die_kd >0: self.die_kd -= delta
            else: self.delete()
        if not self.on_ground:
            self.yspeed += self.gravity*k
            
        else:
            if abs(self.xspeed) > 0.1:
                self.xspeed = self.xspeed * (1 - self.friction)
            else: self.xspeed =0

        if self.yspeed: self.rect.y += self.yspeed *k
        if blocks and self.collision: self._collide_y(blocks)
        if self.xspeed: self.rect.x += self.xspeed *k
        if blocks and self.collision: self._collide_x(blocks)
        if self.collision: self._collide_actors(actors)
        self.pre_rect.center = self.rect.center
    
    def delete(self):
        # print('del', self)
        self._delete = True

    def check_on_ground(self, blocks):
        self.rect.y += 1
        for b in blocks:
            if self.rect.colliderect(b.rect):
                self.rect.y -= 1
                return True
        self.rect.y -= 1
        return False
    
    def check_right(self, blocks):
        self.rect.x += 1
        for b in blocks:
            if self.rect.colliderect(b.rect):
                self.rect.x -= 1
                return True
        self.rect.x -= 1
        return False
    
    def check_left(self, blocks):
        self.rect.x -= 1
        for b in blocks:
            if self.rect.colliderect(b.rect):
                self.rect.x += 1
                return True
        self.rect.x += 1
        return False

    def _collide_x(self, blocks):
        if self.xspeed == 0: return
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
        if self.yspeed == 0: return
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
    def _collide_actors(self, actors):
        [self.hit(a) for a in actors if self.rect.colliderect(a.rect) and a != self]
    
    def hit(self, actor):
        pass
    def draw(self, screen:pg.Surface, camera:pg.Rect):
        # pg.draw.circle(screen, 'green',(self.rect.centerx - camera.x, self.rect.centery + camera.y,), 20)
        # screen.fill('red',(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h))
        if not self.visible: return
        if self.img:
            screen.blit(self.img, real(self.rect.topleft, camera))
        else:
            screen.fill('red',real(self.rect,camera))
    
    def nothing(self,*args,**kwargs):
        pass

