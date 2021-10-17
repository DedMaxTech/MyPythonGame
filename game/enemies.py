import pygame as pg
import math
from game.level import block_s
from random import randint as rd
from game.utils import *
from game.core import Actor

import cfg

SPEED = 3

class AI(Actor):
    START_AGR = 150
    GO_R = 'r'
    GO_L = 'l'
    WAIT = 'w'
    FOLLOW = 'f'

    def __init__(self, x, y):
        super().__init__(x, y, 30,80, friction=0)
        self.look_r = True
        self.jump = False
        self.state = self.WAIT
        self.timer = rd(1000,3000)
    
    def update_ai(self,player_pos, delta):
        self.timer -= delta
        if self.timer <=0:
            states = [self.WAIT]
            if not self.right: states += self.GO_R
            if not self.left: states += self.GO_L
            self.state = states[rd(0,len(states)-1)]
            print(self.state)
            self.timer = rd(1000,3000)
        d = distanse(player_pos,self.rect.center)
        # if d < self.START_AGR and abs(player_pos[0]-self.rect.x):
        #     if player_pos[0]-self.rect.x>0:
        #         if not self.right:self.xspeed = SPEED
        #         else: self.jump = True
        #     else: 
        #         if not self.left:self.xspeed = -SPEED
        #         else: self.jump = True
        # else: self.xspeed = 0
        if d < self.START_AGR and abs(player_pos[0]-self.rect.x) > 20:
            self.state = self.FOLLOW


        match self.state:
            case self.WAIT:
                self.xspeed = 0
            case self.GO_R:
                self.xspeed = SPEED
            case self.GO_L:
                self.xspeed = -SPEED
            case self.FOLLOW:
                if player_pos[0]-self.rect.x>0:self.xspeed = SPEED
                else: self.xspeed = -SPEED
        if self.xspeed != 0:
            if self.right or self.left:
                self.jump = True
        if self.jump and self.on_ground:
            self.jump = False
            self.yspeed = -12
            self.on_ground = False
