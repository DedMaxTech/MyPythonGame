import pygame as pg
import math
from level import block_s
from random import randint

import cfg

PLAYER_IMG = pg.image.load('content/player/player.png')
PLAYER_LEGS_IDLE = pg.image.load('content/player/legs/idle.png')
PLAYER_LEGS_AIR = pg.image.load('content/player/legs/air.png')
PLAYER_LEGS_L = pg.image.load('content/player/legs/left.png')
PLAYER_LEGS_R = pg.image.load('content/player/legs/right.png')
BULLET_IMG = pg.image.load('content/player/guns/bullet.png')

PLAYER_ACCELERATION = 5
PLAYER_MAX_SPEED = 5
JUMP_FORCE = 12
GRAVITY = 0.4

GUNS = {
    'rifle': {'img': pg.image.load('content/player/guns/rifle.png'),
              'hold_img': 0,
              'pos': (29, 29),
              'bull_pos': (0, 0),
              'speed': 30,
              'mag': 30,
              'auto': True},
    'pistol': {'img': pg.image.load('content/player/guns/pistol.png'),
               'hold_img': 0,
               'pos': (29, 29),
               'bull_pos': (0, 0),
               'speed': 30,
               'mag': 10,
               'auto': True},
}


class Bullet():
    def __init__(self, x, y, xv, yv, img, ):
        self.rect = pg.Rect(x, y, 3, 5)
        self.xv, self.yv = xv, yv
        self.img = pg.transform.rotate(img, math.degrees(math.atan(yv / xv)))

    def draw(self, screen: pg.Surface):
        screen.blit(self.img, self.rect.topleft)


class Player(object):
    def __init__(self, x, y, n=0, game_inst=None):
        self.n = n
        self.s = {}
        self.game = game_inst
        # pg.sprite.Sprite.__init__(self)
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
        self.bullets = []

    def process_move(self, d: dict):
        if d.get('right') is not None:
            self.move_right = d['right']
        if d.get('left') is not None:
            self.move_left = d['left']
        if d.get('up') is not None:
            self.jump = d['up']
        if d.get('look_r') is not None:
            self.look_r = d['look_r']
        if d.get('shoot') is not None:
            self.shoot()

    def update(self, blocks, level):
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
        for b in self.bullets:
            b.rect.x += b.xv
            b.rect.y += b.yv
            for i in blocks:
                if pg.sprite.collide_rect(b, i):
                    print(len(self.bullets))
                    if i.type in [i for i in block_s if block_s[i]['dest']]: level.set_block(b.rect.topleft, '0')
                    del self.bullets[self.bullets.index(b)]
                    break

        # if self.rect.y > cfg.screen_v: self.game.death()

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

    def shoot(self):
        b = Bullet(self.rect.x + GUNS[self.gun]['pos'][0],
                   self.rect.y + GUNS[self.gun]['pos'][1],
                   GUNS[self.gun]['speed'] if self.look_r else -GUNS[self.gun]['speed'],
                   randint(-2, 3),
                   BULLET_IMG)
        self.bullets.append(b)

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

        screen.blit(self.img,
                    (self.rect.x - camera.x if self.look_r else self.rect.x - camera.x - 30, self.rect.y + camera.y))
        for b in self.bullets:
            screen.blit(b.img, (b.rect.x - camera.x, b.rect.y + camera.y))
