from typing import List, Union
import pygame as pg

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


class Block:
    def __init__(self, x, y, t):
        # pg.sprite.Sprite.__init__(self)
        self.img: pg.Surface = None
        self.type = t
        self.set_type(t)
        self.rect = self.img.get_rect()
        self.rect.x = x;
        self.rect.y = y

    def set_type(self, t):
        self.type = t
        self.img = pg.image.load(block_s[t]['img']).convert_alpha()

    def __str__(self):
        return f'{self.type} {self.rect.x} {self.rect.y}'


class World:
    def __init__(self, level=None):
        self.levelname = level
        self.h, self.w = 0, 0
        self.blocks: List[Block] = []
        self.actors = []
        self.bg_name = 'game/content/blocks/bg.png'
        # self.bg = pg.image.load(self.bg_name).convert()
        self.rect: pg.Rect = None
        if level: self.open_world(level)

    def open_world(self, level, prepared=False, video=True):
        level = level
        if not prepared:
            with open(level, 'r') as file:
                self.level = level
                self.blocks = []
                level = file.readlines()
        self.bg_name = level[0][:-1]
        if video:self.bg = pg.image.load(self.bg_name).convert()
        else:self.bg = pg.image.load(self.bg_name)
        level = level[1:]
        self.h = len(level)
        for line in level:
            t, x, y = line.split(' ')
            x, y = int(x), int(y)
            if self.w < x: self.w = x
            b = Block(x, y, t)
            self.blocks.append(b)
        self.rect = pg.Rect(0, 0, self.get_size()[0], self.get_size()[1])
        # print(f'Level opened: {level}')

    def save_world(self, levelname):
        with open(levelname, 'w') as file:
            file.write(f'{self.bg_name}\n')
            for b in self.blocks:
                file.write(f'{b.__str__()}\n')

    def get_blocks(self, rect:pg.Rect=None):
        if rect is None:
            return self.blocks
        return [self.blocks[i] for i in rect.collidelistall(self.blocks)]

    def update_actors(self, delta):
        for a in self.actors:
            if a._delete:
                del self.actors[self.actors.index(a)]
                continue
            a.update(delta, self.get_blocks(a.pre_rect))

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
        [a.draw(screen, camera) for a in self.actors]