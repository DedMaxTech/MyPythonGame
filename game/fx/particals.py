import pygame as pg
from game import core

class BloodParticle(core.Actor):
    def __init__(self, x, y, w, xv,yv):
        super().__init__(x, y, w, w,friction=0,collision=False)
        self.xspeed, self.yspeed = xv,yv
        self.autodel(1)
