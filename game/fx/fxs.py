from .particals import *
from random import randint as rd

def blood(pos,world, amount=10):
    x,y = pos
    for i in range(amount):
        world.actors.append(BloodParticle(x,y,3,rd(-1,1),rd(0,3)))

def damage(pos, dmg, world):
    x,y = pos
    world.actors.append(DamageParticle(x,y,dmg,abs(dmg),rd(-1,1),3))


