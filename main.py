import pygame as pg
import os
import traceback

import cfg, player, level
from UI import Interface, Button


from editor import Editor


class Game:
    def __init__(self):
        self.res, self.fps = [cfg.screen_h, cfg.screen_v], cfg.fps
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        pg.init()

        self.screen = pg.display.set_mode(size=self.res, flags=pg.SCALED ,vsync=True)
        self.clock = pg.time.Clock()
        self.camera = pg.Rect(0, 40, self.res[0], self.res[1])
        self.ui = Interface()
        self.level = level.Level()

        self.playing = False  # TODO: меню

        pg.display.set_caption(cfg.GAMENAME)
        pg.display.toggle_fullscreen()
        self.main_menu()
        pg.time.set_timer(pg.USEREVENT, 100)

    def main_menu(self):
        self.screen.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        self.ui.set_ui([
            Button((100, 100), 'white', 'MENU', 80, ),
            Button((150, 200), 'white', 'New game', 50, self.start_game, 'darkgrey'),
            Button((150, 260), 'white', 'Level editor', 50, self.editor, 'darkgrey'),
            Button((150, 320), 'white', 'Exit', 50, exit, 'darkgrey'),
        ])

    def pause_menu(self):
        self.ui.clear()
        if self.playing:
            self.playing = False
            self.ui.set_ui([
                Button((500, 200), 'white', 'Continue', 50, self.pause_menu, 'darkgrey'),
                Button((500, 260), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'),
                Button((500, 320), 'white', 'Exit', 50, exit, 'darkgrey'),
            ])
        else:
            self.playing = True

    def editor(self):
        pg.display.set_caption('для продолженя игры закройте редактор')
        pg.display.toggle_fullscreen()
        os.system('python editor.py')
        pg.display.toggle_fullscreen()
        pg.display.set_caption(cfg.GAMENAME)

    def start_game(self):
        self.ui.clear()
        self.level.open_level('levels/level.txt')
        self.playing = True
        self.player = player.Player(50, 0, self)
        self.camera.x = 0

    def death(self):
        self.playing = False
        pg.time.delay(500)
        for i in range(256):
            self.screen.fill('black', [0, 0, self.res[0], self.res[1] + 40])
            self.ui.clear()
            self.ui.set_ui([
                Button((350, 200), (i, 0, 0), 'GAME OVER', 80, ),
            ])
            self.draw()
            pg.display.update()
            pg.time.delay(10)
        self.ui.set_ui([
            Button((500, 300), 'white', 'Try again', 50, self.start_game, 'darkgrey'),
            Button((500, 360), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'),
            Button((500, 420), 'white', 'Exit', 50, exit, 'darkgrey'),
        ])

    def camera_update(self):
        if self.player.rect.x < self.camera.x + 200 and self.camera.x > 0:
            self.camera.x -= self.camera.x + 200 - self.player.rect.x
        if self.player.rect.right > self.camera.right - 200 and self.camera.right < self.level.rect.right:
            self.camera.x += self.player.rect.right - self.camera.right + 200

    def draw(self):
        self.ui.draw(self.screen)
        if self.playing:
            self.level.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            # if event.type in [pg.KEYDOWN, pg.K_RETURN] and self.playing == False:
            #     self.start_game()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.ui.update_buttons(event)

            if self.playing:
                self.player.update_control(event, self.camera)

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.pause_menu()

    def loop(self):

        self.event_loop()
        if self.playing:
            self.player.update(self.level.get_blocks(), self.level)

            self.camera_update()

        self.draw()
        pg.display.update()

    def run(self):
        while True:
            self.loop()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except Exception as e:
        print(traceback.format_exc())
        pg.display.toggle_fullscreen()
