import pygame as pg

PLAYER_IMG = pg.image.load('content/player.png')
PLAYER_IMG_AIR = pg.image.load('content/player_air.png')

PLAYER_ACCELERATION = 5
PLAYER_MAX_SPEED = 5
JUMP_FORCE = 15
GRAVITY = 0.5


class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.xvel, self.yvel = 0, 0
        self.img = PLAYER_IMG
        self.rect = self.img.get_rect()

        self.rect.x = x;
        self.rect.y = y
        self.move_left, self.move_right, self.jump = False, False, False
        self.on_ground = False
        self.look_r = True
        self.air_log = []
        self.timer = 0

    def update_control(self, event: pg.event.Event):

        # if key[pg.K_d] and self.xvel < PLAYER_MAX_SPEED:
        #     self.xvel += PLAYER_ACCELERATION
        # if key[pg.K_a] and self.xvel > -PLAYER_MAX_SPEED:
        #     self.xvel -= PLAYER_ACCELERATION
        # if not key[pg.K_a] and not key[pg.K_d]:
        #     print('hjr')
        #     if self.xvel > 0: self.xvel -= PLAYER_ACCELERATION
        #     if self.xvel < 0: self.xvel += PLAYER_ACCELERATION
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d: self.move_right = True
            if event.key == pg.K_a: self.move_left = True
            if event.key == pg.K_SPACE: self.jump = True
        if event.type == pg.KEYUP:
            if event.key == pg.K_d: self.move_right = False
            if event.key == pg.K_a: self.move_left = False
            if event.key == pg.K_SPACE: self.jump = False

    def update(self, blocks):
        # багованый вариант с инерцией
        # self.timer += delta
        # if self.timer >=250:
        #     self.timer = 0
        #     if self.move_right and self.xvel < PLAYER_MAX_SPEED: self.xvel += PLAYER_ACCELERATION
        #     if self.move_left and self.xvel > -PLAYER_MAX_SPEED: self.xvel -= PLAYER_ACCELERATION
        #     if not self.move_right and not self.move_left:
        #         if self.xvel > 0: self.xvel -= PLAYER_ACCELERATION * 2
        #         if self.xvel < 0: self.xvel += PLAYER_ACCELERATION * 2
        if self.move_right: self.xvel = PLAYER_ACCELERATION
        if self.move_left: self.xvel = -PLAYER_ACCELERATION
        if not self.move_right and not self.move_left: self.xvel = 0

        if self.jump and self.on_ground:
            self.jump = False
            self.yvel = -JUMP_FORCE
            self.on_ground = False
        if not self.on_ground: self.yvel += GRAVITY

        self.move(blocks)

        self.air_log.append(self.on_ground)


    def collide_x(self, blocks):
        for b in blocks:
            if pg.sprite.collide_rect(self, b):
                if self.move_right:
                    self.rect.right = b.rect.left
                if self.move_left:
                    self.rect.left = b.rect.right

    def collide_y(self, blocks):
        global touch_ground
        touch_ground = False
        for b in blocks:
            if pg.sprite.collide_rect(self, b):
                if self.yvel > 0:
                    self.yvel = 0
                    self.rect.bottom = b.rect.top
                    touch_ground = True
                if self.yvel < 0:
                    self.yvel = 0
                    self.rect.top = b.rect.bottom
        self.on_ground = touch_ground

    def move(self, blocks):
        self.rect.y += self.yvel
        self.collide_y(blocks)
        self.rect.x += self.xvel
        self.collide_x(blocks)

    def rotate(self):
        self.img = pg.transform.flip(self.img, True, False)
        self.look_r = not self.look_r

    def draw(self, screen: pg.Surface, camera:pg.Rect):
        # self.img = PLAYER_IMG if self.on_ground else PLAYER_IMG_AIR
        if not self.look_r and self.xvel > 0: self.rotate()
        if self.look_r and self.xvel < 0: self.rotate()

        screen.blit(self.img, (self.rect.x-camera.x, self.rect.y))
