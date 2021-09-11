from typing import Union
import pygame as pg

img_rock = 'content/block_rock.png'
img_wood = 'content/block_wood.png'
img_leaves = 'content/block_leaves.png'
img_lastick = 'content/block_nthg.png'

block_s = {
    '0':img_lastick,
    '=':img_rock,
    '|':img_wood,
    '+':img_leaves
}


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, t):
        pg.sprite.Sprite.__init__(self)
        self.img = None
        self.type = t
        self.set_type(t)
        self.rect = self.img.get_rect()
        self.rect.x = x; self.rect.y = y

    def set_type(self, t):
        self.type = t
        self.img = pg.image.load(block_s[t])

    def __str__(self):
        return f'{self.type} {self.rect.x} {self.rect.y}'


class Level:
    def __init__(self, level=None):
        self.levelname = level
        self.h, self.w = 0, 0
        self.blocks = []
        self.bg = 'content/bg.png'
        self.rect:pg.Rect = None
        if level: self.open_level(level)

    def open_level(self, levelname):
        with open(levelname, 'r') as file:
            self.levelname = levelname
            self.blocks = []
            level = file.readlines()
            self.bg = level[0][:-1]; level = level[1:]
            self.h = len(level)
            for line in level:
                t, x, y = line.split(' '); x,y = int(x), int(y)
                if self.w < x: self.w = x
                b = Block(x, y, t)
                self.blocks.append(b)
            self.rect = pg.Rect(0, 0, self.get_size()[0], self.get_size()[1])

    def save_level(self, levelname):
        with open(levelname, 'w') as file:
            file.write(f'{self.bg}\n')
            for b in self.blocks:
                file.write(f'{b.__str__()}\n')


    def get_blocks(self):

        return self.blocks

    def set_blocks(self, blocks):
        self.blocks = blocks

    def set_block(self, pos, t):
        flag = True
        print(len(self.blocks))
        for b in self.blocks:
            if pg.Rect.collidepoint(b.rect, pos[0], pos[1]):
                if t == '0':
                    del self.blocks[self.blocks.index(b)]
                else:
                    b.set_type(t)
                    flag = False
        if flag and pos[1] >= 0 and t !='0':
            b = Block(pos[0]//40*40,pos[1]//40*40,t)
            self.blocks.append(b)

    def get_size(self):
        return (self.w + 40), self.h

    def draw(self, screen:pg.Surface, camera:pg.Rect):
        screen.blit(pg.image.load(self.bg), (0,camera.y))
        for i in self.blocks:
            screen.blit(i.img, (i.rect.x - camera.x, i.rect.y + camera.y))
