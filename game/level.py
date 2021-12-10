from typing import List, Union
import pygame as pg
import sys,importlib
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

conf = '''# Full auto-generated, can be edited
from game import *

spawn_pos = (40,40)
background = '{bg}'
guns = []


ais = [

]

actors=[

]

blocks = [

]
'''

def write_list(name, arr):
    separator = ',\n\t'
    return f"{name} = [\n\t{separator.join(arr)}\n]\n"

# def get_copyes(arr):
#     return [copy(i) for i in arr]

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
        return f'level.Block({self.rect.x},{self.rect.y},{repr(self.type)})'


class World(core.Saving):
    slots = {
        # 'spawn_x':['spawn_pos[0]', int],
        # 'spawn_y':['spawn_pos[1]', int],
        # 'spawn_pos':['spawn_pos',list],
        'background':['bg_name',str],
        'guns':['guns',list],
    }
    def __init__(self, level=None):
        self.levelname = level
        self.h, self.w = 0, 0
        self.blocks: List[Block] = []
        self.actors: List[core.Actor] = []
        self.ais: List[enemies.MeleeAI] = []
        self.images: List[pg.Surface] = []
        self.guns = []
        self.ignore_str = []
        self.spawn_pos = (40,40)
        self.bg_name = 'game/content/blocks/bg.png'
        # self.bg = pg.image.load(self.bg_name).convert()
        self.rect: pg.Rect = None
        if level: self.open_world(level)

    def open_world(self, levelname, game_inst=None, video=True):
        self.actors, self.images, self.ais, self.ignore_str = [],[], [], ''
        # with open(f'levels/{levelname}.py', 'r') as file:
        #     self.ignore_str, _ = ''.join(file.readlines()).split('####DONT TOUCH####')
        level = importlib.import_module(f'levels.{levelname}')
        # if f'levels.{levelname}' in sys.modules:
        importlib.reload(level)
        # exec(f'from levels import {level}')
        print(f'{video=}')
        self.bg_name = level.background
        if video:self.bg = pg.image.load(level.background).convert()
        else:self.bg = pg.image.load(level.background)
        self.spawn_pos = level.spawn_pos
        self.guns = level.guns.copy()
        self.ais = level.ais.copy()
        self.actors = level.actors.copy()+self.ais
        [a.set_game(game_inst) for a in self.actors]
        # print([(a,a._delete) for a in self.actors])
        for a in self.actors: 
            if isinstance(a, objects.BaseTriger): a.game = game_inst
        self.blocks = level.blocks.copy()
        self.rect = pg.Rect(0, 0, self.get_size()[0], self.get_size()[1])
        # print(f'Level opened: {level}')
        return self.spawn_pos, self.guns

    def save_world(self, levelname):
        with open(f'levels/{levelname}.py', 'w') as file:
            file.write(f'from game import *\n\nspawn_pos = {repr(self.spawn_pos)}\nbackground = {repr(self.bg_name)}\n'+write_list('guns', self.guns))
            # file.write('####DONT TOUCH####\n# Auto-generated in '+__name__+'\n')
            ais = write_list('ais',[i.save() for i in self.ais if isinstance(i,core.Saving)])
            acts = write_list('actors',[i.save() for i in self.actors if isinstance(i,core.Saving) and not isinstance(i, enemies.BaseAI)])
            bs = write_list('blocks', [b.__str__() for b in self.blocks])
            file.write(ais)
            file.write(acts)
            file.write(bs)

    def get_nearest(self, obj_class, pos):
        objcts = [a for a in self.actors if isinstance(a,obj_class)]
        if not objcts: return
        act, min_dist = objcts[0], distanse(objcts[0].rect, pos)
        for a in objcts:
            d = distanse(a.rect, pos)
            if d<min_dist:
                min_dist = d
                act = a
        return act
    
    def get_colliding(self, pos, obj_class=core.Actor):
        return [a for a in self.actors if isinstance(a,obj_class) and a.rect.collidepoint(*pos)]

    def get_blocks(self, rect:pg.Rect=None):
        if rect is None:
            return self.blocks
        return [self.blocks[i] for i in rect.collidelistall(self.blocks)]
        # return self.blocks
    
    def get_actors(self, rect:pg.Rect=None):
        if rect is None:
            return self.actors
        return [self.actors[i] for i in rect.collidelistall(self.actors)]

    def update_actors(self, delta, player = None):
        delta = limit(delta, max=30)
        for b in self.blocks:
            if b._delete:
                del self.blocks[self.blocks.index(b)]
        for a in self.actors:
            if a._delete:
                try: del self.actors[self.actors.index(a)]
                except ValueError:continue
            else:
                if not a.static and a.collision:
                    a.update(delta, self.get_blocks(a.pre_rect), self.get_actors(a.pre_rect))
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
        for i in self.get_blocks(camera):
            screen.blit(i.img, (i.rect.x - camera.x, i.rect.y - camera.y))
        for sf,_, pos in self.images: screen.blit(sf, real(pos, camera))
        [a.draw(screen, camera) for a in self.actors]

    def reset(self):pass