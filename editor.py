import pygame as pg
from glob import glob

import cfg, level
from UI import Interface, Button

class Editor:
    def __init__(self):
        self.res, self.fps = [cfg.screen_h, cfg.screen_v], cfg.fps
        pg.init()

        self.screen = pg.display.set_mode(self.res)
        self.clock = pg.time.Clock()
        self.ui = Interface()

        pg.display.set_caption('Editor')

        bs = []; a=0
        for i in glob('levels/level*.txt'):
            bs.append(Button((100, 100+a*45), 'white', i, self.open_level, 30, 'red', args=(i))); a+=1
        self.ui.set_ui(bs)
        self.run()
    
    def open_level(self, level_name):
        with open(level_name, 'r') as lvl:
            for row in lvl.readlines():
                for i in row:
                    pass


    def draw(self):
        self.ui.draw(self.screen)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.ui.update_buttons(event)

    def loop(self):
        self.event_loop()

        self.draw()
        pg.display.update()

    def run(self):
        while True:
            self.loop()
            self.clock.tick(self.fps)