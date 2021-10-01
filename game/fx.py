import pygame as pg

class Fx(pg.sprite.Sprite):
    def __init__(self, x, y, img, c):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.c = c

    def update(self, e):
        if e.type == pg.USEREVENT:
            self.c -= 1
