import pygame as pg

img_rock = 'content/block_rock.png'
img_wood = 'content/block_wood.png'
img_leaves = 'content/block_leaves.png'


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, img):
        pg.sprite.Sprite.__init__(self)
        self.img = pg.image.load(img)
        self.rect = self.img.get_rect()
        self.rect.x = x * self.rect.width
        self.rect.y = y * self.rect.height

    def get_pos(self):
        return self.rect.x, self.rect.y,


class Level:
    def __init__(self, level: [str, list]):
        self.h, self.w = 0, 0
        if type(level) == str:
            with open(level, 'r') as file:
                global leveldata
                leveldata = file.readlines()
        else:
            leveldata = level

        self.blocks = []
        self.h = len(leveldata)
        for row in range(self.h):
            a = len(leveldata[row])
            if self.w < a: self.w = a
            for i in range(a):
                b = leveldata[row][i]
                if b == '=':
                    b = Block(i, row, img_rock)
                    self.blocks.append(b)
                if b == '|':
                    b = Block(i, row, img_wood)
                    self.blocks.append(b)
                if b == '+':
                    b = Block(i, row, img_leaves)
                    self.blocks.append(b)

        self.rect = pg.Rect(0, 0, self.get_size()[0], self.get_size()[1])

    def get_blocks(self):
        return self.blocks

    def set_blocks(self, blocks):
        self.blocks = blocks

    def get_size(self):
        return (self.w - 1) * 40, self.h * 40
