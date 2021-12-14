from types import FunctionType
import pygame as pg
import json
from . utils import *
import cfg

def_tick=1/60*1000

class Saving:
    slots = {}
    module = 'objects'
    def _get_att_val(self,text):
        vals = text.split('.')
        if len(vals)==1: return getattr(self,text)
        last=getattr(self, vals[0])
        for i in text.split('.')[1:]:
            last = getattr(last, i)
        return last
    
    def _set_att_val(self, att, val):
        atts = att.split('.')
        if len(atts)==1: setattr(self, att, val);return
        setattr(self._get_att_val('.'.join(atts[:-1])), atts[-1], val)

    def edit(self, attr, val:str):
        tip = self.slots[attr][1]
        if tip==dict:val = json.loads(val.replace("'",'"'))
        elif tip==list:val = [i.strip() for i in val.split(',') if i]
        elif tip==FunctionType:val = val
        elif tip==int: val=int(val)
        elif tip==float: val=float(val)
        self._set_att_val(self.slots[attr][0],val)
        self.reset()

    def save(self):
        return f'{self.module}.{self.__class__.__name__}({", ".join(["{key}={val}".format(key=key, val=repr(self._get_att_val(val[0]))) for key,val in self.slots.items()])})'

font = pg.font.SysFont('Arial',size=40)
font.bold=True

class Actor:
    def __init__(self, x, y, w, h, bounce=0.0, gravity=0.4, static=False, friction=0.005, collision=True, image=None, damaging=False):
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

        self.damaging = damaging
        self.hp=100
        self.max_hp=100

        text = font.render(self.__class__.__name__, False, 'red')
        sf = pg.transform.scale(pg.transform.rotate(text.copy(), 45),(w,h))
        sf.blit(pg.transform.scale(pg.transform.rotate(text.copy(), -45),(w,h)), (0,0))
        pg.draw.rect(sf,'red',(0,0,w,h), 2)
        sf.set_alpha(100)
        self.debug_img = sf
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

    def health(self,hp):
        self.hp = limit(self.hp+hp,0,self.max_hp)
        if hp<0: self.damaged(hp)
        if self.hp==0: self.to_death()
    
    def damaged(self, hp):pass
    def to_death(self):pass

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
    
    def debug_draw(self,screen, camera):
        screen.blit(pg.transform.scale(self.debug_img, self.rect.size), real(self.rect.topleft, camera))

    def nothing(self,*args,**kwargs): pass
    def reset(self):pass

