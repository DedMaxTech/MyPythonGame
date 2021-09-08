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

        self.x_loc = 0

    def manage_buttons(self, event):
        b = UI.Button([2, 3], 'black', 'gnjfgdg', self.draw, 'fdf', )

    def start_game(self):
        self.playing = True
        self.player = player.Player(50, 50)
        self.level = level.Level('levels/level2.txt')

    def camera(self):
        if self.player.rect.x < 200 and self.x_loc > 0:
            bs = self.level.blocks
            d = 200 - self.player.rect.x
            for b in bs:
                b.rect.x += d
            self.x_loc += d
        if self.player.rect.x > self.res[0] - 200 and self.x_loc < self.level.rect.right:
            bs = self.level.blocks
            d = self.player.rect.x + 200 - self.res[0]
            for b in bs:
                b.rect.x -= d
            self.x_loc -= d
            print('lol')
        pg.display.set_caption(f'{self.x_loc=} {self.player.rect.x=} {self.res[0] - 200=}')

    def draw(self):
        if self.playing:
            self.screen.blit(pg.image.load('content/bg.png'), (0, 0))
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

        self.event_loop()
        if self.playing:
            self.player.update(self.level.get_blocks())

            self.camera()


        self.draw()
        pg.display.update()
        self.clock.tick(self.fps)


    def run(self):
        while True:
            self.loop()


if __name__ == '__main__':
    game = Game()
    game.run()
