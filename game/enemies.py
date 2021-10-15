import pygame as pg
import math
from game.level import block_s
from random import randint as rd
from game.utils import *
from game.core import Actor

import cfg

class AI(Actor):
    START_AGR = 300

    def __init__(self, x, y):
        super().__init__(x, y, 30,80, friction=0)
        self.look_r = True
        self.jump = False
    
    def update_ai(self,player_pos):
        d = distanse(player_pos,self.rect.center)
        if d < self.START_AGR and abs(player_pos[0]-self.rect.x):
            if player_pos[0]-self.rect.x>0:
                if not self.right:self.xspeed = 3
                else: self.jump = True
            else: 
                if not self.left:self.xspeed = -3
                else: self.jump = True
        else: self.xspeed = 0

        if self.jump and self.on_ground:
            self.jump = False
            self.yspeed = -12
            self.on_ground = False
