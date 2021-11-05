from typing import List, Union
import pygame as pg

from . import enemies,core, objects
from . utils import *

img_rock = 'game/content/blocks/block_rock.png'
img_wood = 'game/content/blocks/block_wood.png'
img_leaves = 'game/content/blocks/block_leaves.png'
img_lastick = 'game/content/blocks/block_nthg.png'
img_metal = 'game/content/blocks/block_metal.png'
img_glass = 'game/content/blocks/block_glass.png'

block_s = {
    '0': {'img': img_lastick, 'dest': False},
    '=': {'img': img_rock, 'dest': False},
    '|': {'img': img_wood, 'dest': False},
    '+': {'img': img_leaves, 'dest': True},
    '-': {'img': img_metal, 'dest': False},
    '/': {'img': img_glass, 'dest': True},
}


class Block(core.Actor):
    def __init__(self, x, y, t):
        super().__init__(x,y,40,40, static=True)
        self.img: pg.Surface = None
        self.type = t
        self.set_type(t)

    def set_type(self, t):
        self.type = t
        self.img = pg.image.load(block_s[t]['img']).convert_alpha()

    def __str__(self):
        return f'b {self.type} {self.rect.x} {self.rect.y}'


class World:
    def __init__(self, level=None):
        self.levelname = level
        self.h, self.w = 0, 0
        self.blocks: List[Block] = []
        self.actors: List[core.Actor] = []
        self.ais: List[enemies.MeleeAI] = []
        self.images: List[pg.Surface] = []
        self.ignore_str = []
        self.spawn_pos = (40,40)
        self.bg_name = 'game/content/blocks/bg.png'
        # self.bg = pg.image.load(self.bg_name).convert()
        self.rect: pg.Rect = None
        if level: self.open_world(level)

    def open_world(self, level, prepared=False, video=True):
        self.actors, self.images, self.ais, self.ignore_str = [],[], [], []
        level = level
        if not prepared:
            with open(level, 'r') as file:
                self.level = level
                self.blocks = []
                level = file.readlines()
        self.bg_name = level[0][:-1]
        print(f'{video=}')
        if video:self.bg = pg.image.load(self.bg_name).convert()
        else:self.bg = pg.image.load(self.bg_name)
        level = level[1:]
        self.h = len(level)
        self.spawn_pos = (40,40)
        for line in level:
            line = line[:-1]
            if line[0] == 'b':
                _, t, x, y = line.split(' ')
                x, y = int(x), int(y)
                if self.w < x: self.w = x
                b = Block(x, y, t)
                self.blocks.append(b)
            elif line[0] == 'i':
                _, x, y, path = line.split(' ')
                self.images.append((pg.image.load(path).convert_alpha(),path, (int(x), int(y))))
            elif line.startswith('pl') == 'p':
                _, x, y = line.split(' ')
                self.spawn_pos = (int(x), int(y))
            elif line.startswith('ai'):
                self.ignore_str.append(f'{line}\n')
                _, x, y = line.split(' ')
                ai = enemies.ShoterAI(int(x),int(y))
                self.ais.append(ai)
                self.actors.append(ai)
            elif line.startswith('ps'):
                self.ignore_str.append(f'{line}\n')
                _, x1,y1,x2,y2,w,h = line.split(' ')
                self.actors += objects.create_portals((int(x1),int(y1)),(int(x2),int(y2)),(int(w),int(h)))
            # t, x, y = line.split(' ')
            # x, y = int(x), int(y)
            # if self.w < x: self.w = x
            # b = Block(x, y, t)
            # self.blocks.append(b)
        self.rect = pg.Rect(0, 0, self.get_size()[0], self.get_size()[1])
        # print(f'Level opened: {level}')
        return self.spawn_pos

    def save_world(self, levelname):
        with open(levelname, 'w') as file:
            file.write(f'{self.bg_name}\n')
            file.write(f'p {self.spawn_pos[0]} {self.spawn_pos[1]}\n')
            [file.write(l) for l in self.ignore_str]
            for _,path, pos in self.images:
                file.write(f'i {pos[0]} {pos[1]} {path}\n')
            for b in self.blocks:
                file.write(f'{b.__str__()}\n')

    def get_nearest(self, obj_class, pos):
        objcts = [a for a in self.actors if type(a) == obj_class]
        if not objcts: return
        act, min_dist = objcts[0], distanse(objcts[0].rect, pos)
        for a in objcts:
            d = distanse(a.rect, pos)
            if d<min_dist:
                min_dist = d
                act = a
        return act

    def get_blocks(self, rect:pg.Rect=None):
        if rect is None:
            return self.blocks
        return [self.blocks[i] for i in rect.collidelistall(self.blocks)]
    
    def get_actors(self, rect:pg.Rect=None):
        if rect is None:
            return self.actors
        return [self.actors[i] for i in rect.collidelistall(self.actors)]

    def update_actors(self, delta, player = None):
        for b in self.blocks:
            if b.type == '0':
                del self.blocks[self.blocks.index(b)]
        for a in self.actors:
            if a._delete:
                del self.actors[self.actors.index(a)]
            else:
                if not a.static and a.collision:
                    a.update(delta, self.get_blocks(a.pre_rect), self.actors)
                else:
                    a.update(delta, [], self.actors)
        if self.ais:
            [ai.update_ai(delta, self) for ai in self.ais]

    def set_blocks(self, blocks):
        self.blocks = blocks

    def set_block(self, pos, t):
        flag = True
        for b in self.blocks:
            if pg.Rect.collidepoint(b.rect, pos[0], pos[1]):
                if t == '0':
                    del self.blocks[self.blocks.index(b)]
                else:
                    b.set_type(t)
                    flag = False
        if flag and t != '0':
            b = Block(pos[0] // 40 * 40, pos[1] // 40 * 40, t)
            self.blocks.append(b)

    def get_size(self):
        return (self.w + 40), self.h
    
    def draw(self, screen: pg.Surface, camera: pg.Rect):
        screen.blit(self.bg, (0,0))
        for i in self.get_blocks():
            screen.blit(i.img, (i.rect.x - camera.x, i.rect.y - camera.y))
        for sf,_, pos in self.images: screen.blit(sf, real(pos, camera))
        [a.draw(screen, camera) for a in self.actors]
