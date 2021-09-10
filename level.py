from typing import Union
import pygame as pg

img_rock = 'content/block_rock.png'
img_wood = 'content/block_wood.png'
img_leaves = 'content/block_leaves.png'

block_s = {
    '=':img_rock,
    '|':img_wood,
    '+':img_leaves
}


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, t):
        pg.sprite.Sprite.__init__(self)
        self.img = None
        self.set_type(t)
        self.rect = self.img.get_rect()
        self.rect.x = x * self.rect.width
        self.rect.y = y * self.rect.height

    def set_type(self, t):
        self.img = pg.image.load(block_s[t])


class Level:
    def __init__(self, level=None):
        self.h, self.w = 0, 0
        self.blocks = []
        self.bg = 'content/bg.png'
        self.rect:pg.Rect = None
        if level: self.open_level(level)

    def open_level(self, levelname):
        with open(levelname, 'r') as file:
            self.blocks = []
            level = file.readlines()
            self.h = len(level)
            for row in range(self.h):
                a = len(level[row])
                if self.w < a: self.w = a
                for i in range(a):
                    b = level[row][i]
                    if b in block_s:
                        b = Block(i, row, b)
                        self.blocks.append(b)
            self.rect = pg.Rect(0, 0, self.get_size()[0], self.get_size()[1])

    def get_blocks(self):
        return self.blocks

    def set_blocks(self, blocks):
        self.blocks = blocks

    def set_block(self, pos, t):
        flag = True
        for b in self.blocks:
            if pg.Rect.collidepoint(b.rect, pos[0], pos[1]):
                b.set_type(t)
                flag = False
        if flag and pos[1] >= 0:
            print(pos[0]//40*40,pos[1]//40*40,t)
            b = Block(pos[0]//40,pos[1]//40,t)
            self.blocks.append(b)
            print(b.rect.topleft)

    def get_size(self):
        return (self.w - 1) * 40, self.h * 40

    def draw(self, screen:pg.Surface, camera:pg.Rect):
        screen.blit(pg.image.load(self.bg), camera.topleft)
        for i in self.blocks:
            screen.blit(i.img, (i.rect.x + camera.x, i.rect.y + camera.y))
