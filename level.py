import pygame as pg

img = 'content/block.png'


class Block(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.img = pg.image.load(img)
        self.rect = self.img.get_rect()
        self.rect.x = x * self.rect.width
        self.rect.y = y * self.rect.height

    def get_pos(self):
        return (self.rect.x, self.rect.y,)

class Level:
    def __init__(self, level: [str, list]):
        if type(level) == str:
            with open(level, 'r') as file:
                global leveldata
                leveldata = file.readlines()
        else:
            leveldata = level

        self.blocks = []
        for row in range(len(leveldata)):
            for i in range(len(leveldata[row])):
                if leveldata[row][i] == '=':
                    b = Block(i, row)
                    self.blocks.append(b)

    def get_blocks(self):
        return self.blocks
