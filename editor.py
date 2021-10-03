import pygame as pg
from glob import glob
import os

import cfg
from game import  level, utils
from game.UI import Interface, Button


class Editor:
    def __init__(self):
        self.res, self.fps = [cfg.screen_h, cfg.screen_v], cfg.fps
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        pg.init()

        self.screen: pg.Surface = pg.display.set_mode((self.res[0], self.res[1] + 40))
        self.clock = pg.time.Clock()
        self.ui = Interface()
        self.level = level.World()
        self.levelname = ''
        self.camera = pg.Rect(0,40,self.res[0], self.res[1])

        self.editing = False
        self.drawing = False
        self.brush = '='
        self.last_brush = None

        pg.display.set_caption('Editor')

        self.main_menu()

        self.run()

    def main_menu(self):
        self.editing=False
        bs = [];
        a = 0
        bs.append(Button((100,100), 'white', 'Levels:', 80, ),)
        for i in glob('levels/level*.txt'):
            bs.append(Button((150, 200 + a * 45), 'white', i, 30, self.open_level, 'red', args=(i)));
            a += 1
        bs.append(Button((150,600), 'white', 'Exit', 50,exit,'darkgrey'))
        self.ui.set_ui(bs)


    def open_level(self, lvl):
        self.ui.clear()
        self.level.open_world(lvl)
        self.levelname = lvl
        bs = [];
        a = 0
        bs.append(Button((0, 0), 'white', 'SAVE', 35, self.save_level, bg='darkgrey', ))
        bs.append(Button((100, 0), 'white', 'EXIT', 35, self.main_menu, bg='darkgrey', ))
        for i in level.block_s:
            bs.append(Button((200 + a * 45, 0), 'white', '', 40, callback_f=self.set_brush, size=(40, 40),
                             img=level.block_s[i]['img'], args=(i)))
            a += 1
        self.ui.set_ui(bs)
        # self.camera
        self.editing = True

    def save_level(self):
        self.editing = False
        self.level.save_world(self.levelname)
        self.ui.clear()
        self.main_menu()

    def set_brush(self, t):
        self.last_brush = self.brush
        self.brush = t


    def camera_update(self, keys):
        if keys[pg.K_a] and self.camera.x > 0:
            self.camera.x -= 10
        if keys[pg.K_d]:
            self.camera.x += 10
        if keys[pg.K_w] and self.camera.y < 40:
            self.camera.y += 10
        if keys[pg.K_s]:
            self.camera.y -= 10


    def draw(self):
        self.screen.fill('black', [0,0,self.res[0], self.res[1]+40])
        if self.editing:
            self.level.draw(self.screen, self.camera)
        self.ui.draw(self.screen)
        utils.debug(f'{self.camera.x} {self.camera.y}', self.screen, y=50)


    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.ui.update_buttons(event)
                if event.button == pg.BUTTON_RIGHT:
                    self.drawing = True
                if event.button == pg.BUTTON_LEFT:
                    self.level.set_block((event.pos[0] + self.camera.x, event.pos[1]-self.camera.y), self.brush)
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_RIGHT: self.drawing = False
            if event.type == pg.MOUSEMOTION and self.drawing: self.level.set_block(
                (event.pos[0] + self.camera.x, event.pos[1] -self.camera.y),
                self.brush)
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT: self.brush = '0'
            if event.type == pg.KEYUP and event.key == pg.K_LSHIFT: self.brush = self.last_brush
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE: self.set_brush(self.last_brush)

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
