from .particals import *
from random import randint as rd
from . import *

def blood(pos,world, amount=10):
    x,y = pos
    for i in range(amount):
        world.actors.append(BloodParticle(x,y,3,rd(-10,10)/3,rd(0,40)/10))

def damage(pos, dmg, world, heal=False):
    x,y = pos
    world.actors.append(DamageParticle(x,y,dmg,abs(dmg),rd(-1,1),3,heal))

def explosion(pos, world, amount=20):
    for i in range(amount):
        x,y = pos[0]+rd(-amount*4,amount*4),pos[1]-rd(0,amount*4)
        world.actors.append(ExploseParticle(x,y,rd(5,20)))

