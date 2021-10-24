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

class AI(core.Actor):
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
    
    def update_ai(self,player, delta):
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
        d = distanse(player.rect.center,self.rect.center)
        # if d < self.START_AGR and abs(player_pos[0]-self.rect.x):
        #     if player_pos[0]-self.rect.x>0:
        #         if not self.right:self.xspeed = SPEED
        #         else: self.jump = True
        #     else: 
        #         if not self.left:self.xspeed = -SPEED
        #         else: self.jump = True
        # else: self.xspeed = 0
        if player is not None and d < self.START_AGR and abs(player.rect.center[0]-self.rect.x) > 30:
            self.state = self.FOLLOW

        if self.state == self.WAIT:
            self.xspeed = 0
        elif self.state == self.GO_R:
            self.xspeed = SPEED
        elif self.state == self.GO_L:
            self.xspeed = -SPEED
        elif self.state == self.FOLLOW:
            if player.rect.center[0]-self.rect.x>15:self.xspeed = SPEED
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
