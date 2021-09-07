import pygame as pg

import cfg, UI, player, level


class Game:
    def __init__(self):
        self.res, self.fps = [cfg.screen_h, cfg.screen_v], cfg.fps
        pg.init()

        self.screen = pg.display.set_mode(self.res)
        self.clock = pg.time.Clock()
        pg.display.set_caption('MyGoodPythonGame')

        self.playing = False  # TODO: меню

    def manage_buttons(self, event):
        b = UI.Button([2, 3], 'black', 'gnjfgdg', self.draw, 'fdf', )

    def start_game(self):
        self.playing = True
        self.player = player.Player(50, 50)
        self.level = level.Level('level.txt')

    def draw(self):
        if self.playing:
            self.screen.fill('white')
            self.player.draw(self.screen)
            for i in self.level.get_blocks():
                self.screen.blit(i.img, i.get_pos())

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            if event.type in [pg.KEYDOWN, pg.K_RETURN] and self.playing == False:
                self.start_game()

            if event.type in [pg.KEYUP, pg.KEYDOWN] and self.playing:
                self.player.update_control(event)

    def loop(self):
        self.draw()
        self.event_loop()
        if self.playing:
            self.player.update(self.clock.get_time(), self.level.get_blocks())
            pg.display.set_caption(str((self.player.rect.topleft, self.player.xvel, self.player.yvel)))

        pg.display.update()
        self.clock.tick(self.fps)


    def run(self):
        while True:
            self.loop()


if __name__ == '__main__':
    game = Game()
    game.run()
