import pygame as pg

import cfg

PLAYER_IMG = pg.image.load('content/player/player.png')
PLAYER_IMG_AIR = pg.image.load('content/player/player_air.png')

GUN_IMG = pg.image.load('content/gun.png')

PLAYER_ACCELERATION = 5
PLAYER_MAX_SPEED = 5
JUMP_FORCE = 15
GRAVITY = 0.5


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, game_inst):
        self.game = game_inst
        pg.sprite.Sprite.__init__(self)
        self.xspeed, self.yspeed = 0, 0
        self.img = PLAYER_IMG
        self.rect = pg.Rect(x,y,30,60)

        self.move_left, self.move_right, self.jump = False, False, False
        self.on_ground = False
        self.look_r = True
        self.timer = 0

    def update_control(self, event: pg.event.Event, camera:pg.Rect):

        # if key[pg.K_d] and self.xspeed < PLAYER_MAX_SPEED:
        #     self.xspeed += PLAYER_ACCELERATION
        # if key[pg.K_a] and self.xspeed > -PLAYER_MAX_SPEED:
        #     self.xspeed -= PLAYER_ACCELERATION
        # if not key[pg.K_a] and not key[pg.K_d]:
        #     print('hjr')
        #     if self.xspeed > 0: self.xspeed -= PLAYER_ACCELERATION
        #     if self.xspeed < 0: self.xspeed += PLAYER_ACCELERATION
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d: self.move_right = True
            if event.key == pg.K_a: self.move_left = True
            if event.key == pg.K_SPACE: self.jump = True
        if event.type == pg.KEYUP:
            if event.key == pg.K_d: self.move_right = False
            if event.key == pg.K_a: self.move_left = False
            if event.key == pg.K_SPACE: self.jump = False
        if event.type == pg.MOUSEMOTION:
            if self.rect.x <= event.pos[0]+camera.x:
                self.look_r = True
            else: self.look_r = False

    def update(self, blocks):
        self.on_ground = self.check_on_ground(blocks)
        # багованый вариант с инерцией
        # self.timer += delta
        # if self.timer >=250:
        #     self.timer = 0
        #     if self.move_right and self.xspeed < PLAYER_MAX_SPEED: self.xspeed += PLAYER_ACCELERATION
        #     if self.move_left and self.xspeed > -PLAYER_MAX_SPEED: self.xspeed -= PLAYER_ACCELERATION
        #     if not self.move_right and not self.move_left:
        #         if self.xspeed > 0: self.xspeed -= PLAYER_ACCELERATION * 2
        #         if self.xspeed < 0: self.xspeed += PLAYER_ACCELERATION * 2
        if self.move_right: self.xspeed = PLAYER_ACCELERATION
        if self.move_left: self.xspeed = -PLAYER_ACCELERATION
        if not self.move_right and not self.move_left: self.xspeed = 0

        if self.jump and self.on_ground:
            self.jump = False
            self.yspeed = -JUMP_FORCE
            self.on_ground = False
        if not self.on_ground: self.yspeed += GRAVITY

        self.move(blocks)

        if self.rect.y > cfg.screen_v: self.game.death()

    def check_on_ground(self, blocks):
        self.rect.y +=1
        for b in blocks:
            if pg.sprite.collide_rect(self, b):
                self.rect.y -= 1
                return True
        self.rect.y -= 1
        return False


    def collide_x(self, blocks):
        for b in blocks:
            if pg.sprite.collide_rect(self, b):
                if self.move_right:
                    self.rect.right = b.rect.left
                if self.move_left:
                    self.rect.left = b.rect.right

    def collide_y(self, blocks):
        for b in blocks:
            if pg.sprite.collide_rect(self, b):
                if self.yspeed > 0:
                    self.yspeed = 0
                    self.rect.bottom = b.rect.top
                if self.yspeed < 0:
                    self.yspeed = 0
                    self.rect.top = b.rect.bottom

    def move(self, blocks):
        self.rect.y += self.yspeed
        self.collide_y(blocks)
        self.rect.x += self.xspeed
        self.collide_x(blocks)

    def rotate(self):
        self.img = pg.transform.flip(self.img, True, False)


    def draw(self, screen: pg.Surface, camera:pg.Rect):
        self.img = PLAYER_IMG if self.on_ground else PLAYER_IMG_AIR
        self.img.blit(GUN_IMG, (29, 29))
        # if not self.look_r and self.xspeed > 0: self.rotate()
        # if self.look_r and self.xspeed < 0: self.rotate()
        if not self.look_r: self.rotate()

        screen.blit(self.img, (self.rect.x-camera.x if self.look_r else self.rect.x-camera.x-30, self.rect.y))
