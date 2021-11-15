import pygame as pg
import math
# from game.level import block_s
from random import randint as rd
# from .player import Player
from . import player, core
from . utils import *

import cfg

SPEED = 3

AI_IMG_IDLE = pg.image.load('game/content/ai/idle.png')
AI_IMG_RIGHT = pg.image.load('game/content/ai/lookr.png')
AI_IMG_LEFT = pg.transform.flip(AI_IMG_RIGHT, True, False)


class BaseAI(core.Actor):
    def update_ai(self,delta, world):
        pass
    def hit(self, actor):
        if isinstance(actor, player.Player) and self.attack_kd <= 0:
            self.attack_kd = 1000
            dmg = 20
            actor.hp -= dmg
            write_stat('received damage', get_stat('received damage')+dmg)
            actor.dmg_timer = 100
class MeleeAI(BaseAI):
    START_AGR = 250
    GO_R = 'r'
    GO_L = 'l'
    WAIT = 'w'
    FOLLOW = 'f'
    ATTACK = 'a'

    def __init__(self, x, y):
        super().__init__(x, y, 30,80, friction=0)
        self.look_r = True
        self.jump = False
        self.hp = 100
        self.state = self.WAIT
        self.timer = rd(1000,3000)
        self.attack_kd = 0
        self.dmg_timer = 0
        self.need_sides = True
        
    
    def update_ai(self,delta, world):
        if self.hp <=0:
            self.delete()
            return
        self.timer -= delta
        if self.attack_kd >0: self.attack_kd-=delta
        if self.dmg_timer >0: self.dmg_timer-=delta
        if self.timer <=0:
            states = [self.WAIT]
            if not self.right: states += self.GO_R
            if not self.left: states += self.GO_L
            self.state = states[rd(0,len(states)-1)]
            self.timer = rd(1000,3000)
        target = world.get_nearest(player.Player, self.rect.center)
        d = distanse(target.rect.center,self.rect.center)
        # if d < self.START_AGR and abs(player_pos[0]-self.rect.x):
        #     if player_pos[0]-self.rect.x>0:
        #         if not self.right:self.xspeed = SPEED
        #         else: self.jump = True
        #     else: 
        #         if not self.left:self.xspeed = -SPEED
        #         else: self.jump = True
        # else: self.xspeed = 0
        if target is not None and d < self.START_AGR and abs(target.rect.centerx-self.rect.x) > 30:
            self.state = self.FOLLOW

        if self.state == self.WAIT:
            self.xspeed = 0
        elif self.state == self.GO_R:
            self.xspeed = SPEED
        elif self.state == self.GO_L:
            self.xspeed = -SPEED
        elif self.state == self.FOLLOW:
            if target.rect.centerx-self.rect.x>15:self.xspeed = SPEED
            else: self.xspeed = -SPEED
        # match self.state:
        #     case self.WAIT:
        #         self.xspeed = 0
        #     case self.GO_R:
        #         self.xspeed = SPEED
        #     case self.GO_L:
        #         self.xspeed = -SPEED
        #     case self.FOLLOW:
        #         if player_pos[0]-self.rect.x>0:self.xspeed = SPEED
        #         else: self.xspeed = -SPEED
        if self.xspeed != 0:
            if self.right or self.left:
                self.jump = True
        if self.jump and self.on_ground:
            self.jump = False
            self.yspeed = -12
            self.on_ground = False
    
    def hit(self, actor):
        if isinstance(actor, player.Player) and self.attack_kd <= 0:
            self.attack_kd = 1000
            dmg = 20
            actor.hp -= dmg
            write_stat('received damage', get_stat('received damage')+dmg)
            actor.dmg_timer = 100

    def draw(self, screen:pg.Surface, camera:pg.Rect):
        if self.xspeed == 0:img,off = AI_IMG_IDLE.copy(), (0,0)
        else:
            if self.xspeed>0: img,off = AI_IMG_RIGHT.copy(), (0,0)
            else:img,off = AI_IMG_LEFT.copy(), (-30,0)
        # screen.fill('red',(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h))
        pg.draw.line(screen,'green',(self.rect.x - camera.x,self.rect.y-camera.y),(self.rect.x - camera.x+(30*self.hp/100),self.rect.y-camera.y),4)
        if self.dmg_timer > 0:
            img.blit(player.RED_TINT,(0,0),special_flags=pg.BLEND_RGB_ADD)
        screen.blit(img, (self.rect.x - camera.x + off[0], self.rect.y-camera.y+off[1]))

class ShoterAI(BaseAI):
    START_AGR = 350
    GO_R = 'r'
    GO_L = 'l'
    WAIT = 'w'
    ATTACK = 'a'

    def __init__(self, x, y, gun='rifle', moving=False):
        super().__init__(x, y, 30,80, friction=0)
        self.look_r = True
        self.jump = False
        self.hp = 100
        self.state = self.WAIT
        self.timer = rd(1000,3000)
        self.attack_kd = 0
        self.dmg_timer = 0
        self.need_sides = True
        self.moving = moving

        self.gun = gun
        self.shoot_kd = 0

        self.angle = 90
        
    
    def update_ai(self,delta, world):
        if self.hp <=0:
            self.delete()
            return
        if self.moving: self.timer -= delta
        if self.attack_kd >0: self.attack_kd-=delta
        if self.dmg_timer >0: self.dmg_timer-=delta
        if self.shoot_kd>0: self.shoot_kd-=delta
        if self.timer <=0:
            self.pick_state()
            self.timer = rd(1000,3000)

        target = world.get_nearest(player.Player, self.rect.center)
        d = distanse(target.rect.center,self.rect.center)
        x,y = real(self.rect.center,target.rect)
        x,y = -x,y-40
        self.look_r=x>0
        ang = angle((-x,y if x<0 else -y))
        self.angle = ang if x>0 else -ang+180
        self.d = d
        if target is not None and d < self.START_AGR:
            self.state = self.ATTACK
        else: self.pick_state()
        if self.state == self.WAIT:
            self.xspeed = 0
        elif self.state == self.GO_R:
            self.xspeed = SPEED
        elif self.state == self.GO_L:
            self.xspeed = -SPEED
        elif self.state == self.ATTACK:
            self.xspeed = 0
            self.shoot(target, world)

        # match self.state:
        #     case self.WAIT:
        #         self.xspeed = 0
        #     case self.GO_R:
        #         self.xspeed = SPEED
        #     case self.GO_L:
        #         self.xspeed = -SPEED
        #     case self.FOLLOW:
        #         if player_pos[0]-self.rect.x>0:self.xspeed = SPEED
        #         else: self.xspeed = -SPEED
        if self.xspeed != 0:
            if self.right or self.left:
                self.jump = True
        if self.jump and self.on_ground:
            self.jump = False
            self.yspeed = -12
            self.on_ground = False
    
    def shoot(self, target,world):
        if self.shoot_kd >0: return
        
        gun = player.GUNS[self.gun]
        acc = gun['acc']*2
        ang = self.angle+(rd(-acc*5, acc*5)/2)
        xvel, yvel = vec_to_speed(gun['speed'],ang)
        b = player.Bullet(
            self.rect.centerx, self.rect.centery,
            xvel, yvel, gun['bull_img'], ang, gun['dmg']/4, self
        )
        world.actors.append(b)

        self.shoot_kd = gun['kd']*1.5

    def pick_state(self):
        states = [self.WAIT]
        if self.moving:
            if not self.right: states += self.GO_R
            if not self.left: states += self.GO_L
        self.state = states[rd(0,len(states)-1)]

    def hit(self, actor):
        if isinstance(actor, player.Player) and self.attack_kd <= 0:
            self.attack_kd = 1000
            dmg = 20
            actor.hp -= dmg
            write_stat('received damage', get_stat('received damage')+dmg)
            actor.dmg_timer = 100

    def draw(self, screen:pg.Surface, camera:pg.Rect):
        if self.xspeed == 0:img,off = AI_IMG_IDLE.copy(), (0,0)
        else:
            if self.xspeed>0: img,off = AI_IMG_RIGHT.copy(), (0,0)
            else:img,off = AI_IMG_LEFT.copy(), (-30,0)
        # screen.fill('red',(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h))
        pg.draw.line(screen,'green',(self.rect.x - camera.x,self.rect.y-camera.y),(self.rect.x - camera.x+(30*self.hp/100),self.rect.y-camera.y),4)
        gun_img = pg.transform.rotate(player.GUNS[self.gun]['img'].copy(), -self.angle)
        # if not self.look_r: gun_img=pg.transform.flip(gun_img, False,True)
        # debug(gun_img.get_rect().center, screen)
        img.blit(gun_img, (gun_img.get_rect().x, gun_img.get_rect().y+25))
        if self.dmg_timer > 0:
            img.blit(player.RED_TINT,(0,0),special_flags=pg.BLEND_RGB_ADD)
        screen.blit(img, (self.rect.x - camera.x + off[0], self.rect.y-camera.y+off[1]))

