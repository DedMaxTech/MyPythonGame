import pygame as pg

import cfg, player, level
from UI import Interface, Button

from editor import Editor


class Game:
    def __init__(self):
        self.res, self.fps = [cfg.screen_h, cfg.screen_v], cfg.fps
        pg.init()

        self.screen = pg.display.set_mode(self.res)
        self.clock = pg.time.Clock()
        self.camera = pg.Rect(0,0,self.res[0], self.res[1])
        self.ui = Interface()

        self.playing = False  # TODO: меню

        pg.display.set_caption('MyGoodPythonGame')
        self.ui.set_ui([
            Button((200,200), 'white', 'Новая игра', 50, self.start_game,'red'),
            Button((200,260), 'white', 'Редактор', 50, self.editor, 'red'),
            Button((200,320), 'white', 'Выход', 50,exit,'red')
        ])

    def editor(self):
        Editor()
    
    def start_game(self):
        self.ui.clear()
        self.playing = True
        self.player = player.Player(50, 50)
        self.level = level.Level('levels/level2.txt')

    def camera_update(self):
        # if self.player.rect.x < self.camera.x+200 and self.camera.x > 0:
        #     bs = self.level.blocks
        #     d = self.camera.x + 200 - self.player.rect.x
        #     print(d)
        #     for b in bs:
        #         b.rect.x += d
        #     self.camera.x -= d
        # if self.player.rect.right > self.camera.right - 200 and self.camera.right < self.level.rect.right:
        #
        #     bs = self.level.blocks
        #     d = self.camera.right - 200 - self.player.rect.x
        #     print(d)
        #     for b in bs:
        #         b.rect.x -= d
        #     self.camera.x += d
        #
        pg.display.set_caption(f'{self.camera.x=} {self.camera.right=} {self.player.rect.x=}')
        if self.player.rect.x < self.camera.x + 200 and self.camera.x > 0:

            self.camera.x -= self.camera.x + 200 - self.player.rect.x
        if self.player.rect.right > self.camera.right - 200 and self.camera.right < self.level.rect.right:
            self.camera.x += self.player.rect.right - self.camera.right+200

    def draw(self):
        self.ui.draw(self.screen)
        if self.playing:
            self.screen.blit(pg.image.load('content/bg.png'), (0, 0))
            self.player.draw(self.screen, self.camera)
            for i in self.level.get_blocks():
                self.screen.blit(i.img, (i.rect.x-self.camera.x, i.rect.y))

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            # if event.type in [pg.KEYDOWN, pg.K_RETURN] and self.playing == False:
            #     self.start_game()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.ui.update_buttons(event)


            if event.type in [pg.KEYUP, pg.KEYDOWN] and self.playing:
                self.player.update_control(event)

    def loop(self):

        self.event_loop()
        if self.playing:
            self.player.update(self.level.get_blocks())

            self.camera_update()


        self.draw()
        pg.display.update()
        


    def run(self):
        while True:
            self.loop()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    game = Game()
    game.run()
