import pygame as pg
from glob import glob

from pygame.rect import Rect

import cfg, level
from UI import Interface, Button


class Editor:
    def __init__(self):
        self.res, self.fps = [cfg.screen_h, cfg.screen_v], cfg.fps
        pg.init()

        self.screen: pg.Surface = pg.display.set_mode((self.res[0], self.res[1] + 40))
        self.clock = pg.time.Clock()
        self.ui = Interface()
        self.level = level.Level()
        self.camera = pg.Rect(0,40,self.res[0], self.res[1])

        self.editing = False
        self.drawing = False
        self.brush = '='

        pg.display.set_caption('Editor')

        bs = [];
        a = 0
        for i in glob('levels/level*.txt'):
            bs.append(Button((100, 100 + a * 45), 'white', i, 30, self.open_level, 'red', args=(i)));
            a += 1
        self.ui.set_ui(bs)

        self.run()

    def open_level(self, lvl):
        self.ui.clear()
        self.level.open_level(lvl)
        bs = [];
        a = 0
        for i in level.block_s:
            bs.append(Button((100 + a * 45, 0), 'white', '', 40, callback_f=self.set_brush, size=(40, 40),
                             img=level.block_s[i], args=(i)))
            a += 1
        self.ui.set_ui(bs)
        # self.camera
        self.editing = True

    def set_brush(self, t):
        self.brush = t

    def camera_update(self, keys):
        print(self.level.get_size())
        pg.display.set_caption(f'{self.camera.x=} {self.camera.right=}')
        if keys[pg.K_a] and self.camera.x > 0:
            self.camera.x += 10
        if keys[pg.K_d] and self.camera.right > self.level.rect.right:
            self.camera.x -= 10

    def draw(self):
        self.ui.draw(self.screen)
        if self.editing:
            self.level.draw(self.screen, self.camera)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.ui.update_buttons(event)
                if event.button == pg.BUTTON_LEFT:
                    self.level.set_block((event.pos[0], event.pos[1] - 40),self.brush)
                    self.drawing = True
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_LEFT: self.drawing = False
            if event.type == pg.MOUSEMOTION and self.drawing: self.level.set_block((event.pos[0], event.pos[1] - 40),
                                                                                   self.brush)

    def loop(self):
        self.event_loop()

        self.camera_update(pg.key.get_pressed())

        self.draw()
        pg.display.update()

    def run(self):
        while True:
            self.loop()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    ed = Editor()
    ed.run()
