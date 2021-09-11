import pygame as pg
import math

import cfg

PLAYER_IMG = pg.image.load('content/player/player.png')
PLAYER_LEGS_IDLE = pg.image.load('content/player/legs/idle.png')
PLAYER_LEGS_AIR = pg.image.load('content/player/legs/air.png')
PLAYER_LEGS_L = pg.image.load('content/player/legs/left.png')
PLAYER_LEGS_R = pg.image.load('content/player/legs/right.png')

PLAYER_ACCELERATION = 5
PLAYER_MAX_SPEED = 5
JUMP_FORCE = 12
GRAVITY = 0.5

GUNS = {
    'rifle': {'img': pg.image.load('content/rifle.png'),
              'hold_img': 0,
              'pos': (29, 29),
              'bull_pos': (0, 0),
              'speed': 50,
              'mag': 30,
              'auto': True},
    'pistol': {'img': pg.image.load('content/pistol.png'),
               'hold_img': 0,
               'pos': (29, 29),
               'bull_pos': (0, 0),
               'speed': 50,
               'mag': 10,
               'auto': True},
}


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, xv, yv, img,):
        pg.sprite.Sprite.__init__(self)
        pg.Rect(x,y,3,5)
        self.xv, self.yv = xv, yv
        self.img = pg.transform.rotate(img, math.degrees(math.atan(x/y)))

    def update(self, blocks, level):
        self.rect.x += self.xv
        self.rect.y += self.yv
        for b in blocks:
            if pg.sprite.collide_rect(self, b):
                level.set_block(self.rect.topleft, '0')
                del self

    def draw(self, screen:pg.Surface):

        screen.blit(self.img, self.rect.topleft)



class Player(pg.sprite.Sprite):
    def __init__(self, x, y, game_inst):
        self.game = game_inst
        pg.sprite.Sprite.__init__(self)
        self.xspeed, self.yspeed = 0, 0
        self.img = PLAYER_IMG
        self.rect = pg.Rect(x, y, 30, 60)

        self.move_left, self.move_right, self.jump = False, False, False
        self.on_ground = False
        self.look_r = True
        self.r_leg = True
        self.double = True
        self.timer = 0

        self.gun = 'pistol'
        self.ammo = {'rifle': 240, 'pistol': 100}

    def update_control(self, event: pg.event.Event, camera: pg.Rect):

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
            if self.rect.x <= event.pos[0] + camera.x:
                self.look_r = True
            else:
                self.look_r = False
        if event.type == pg.USEREVENT:
            self.r_leg = not self.r_leg

    def update(self, blocks):
        self.on_ground = self.check_on_ground(blocks)
        if self.on_ground:
            self.double = True
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

        if self.jump and (self.on_ground or self.double):
            if not self.on_ground and self.double:
                self.double = False
                self.xspeed = 0
            self.jump = False
            self.yspeed = -JUMP_FORCE
            self.on_ground = False
        if not self.on_ground: self.yspeed += GRAVITY

        self.move(blocks)

        if self.rect.y > cfg.screen_v: self.game.death()

    def check_on_ground(self, blocks):
        self.rect.y += 1
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

    def draw(self, screen: pg.Surface, camera: pg.Rect):
        self.img = PLAYER_IMG.copy()
        if self.on_ground:
            if self.xspeed == 0:
                self.img.blit(PLAYER_LEGS_IDLE, (0, 53))
            else:
                self.img.blit(PLAYER_LEGS_R if self.r_leg else PLAYER_LEGS_L, (0, 53))
        else:
            self.img.blit(PLAYER_LEGS_AIR, (0, 53))
        self.img.blit(GUNS[self.gun]['img'], GUNS[self.gun]['pos'])
        # if not self.look_r and self.xspeed > 0: self.rotate()
        # if self.look_r and self.xspeed < 0: self.rotate()
        if not self.look_r: self.rotate()

        screen.blit(self.img, (self.rect.x - camera.x if self.look_r else self.rect.x - camera.x - 30, self.rect.y))
