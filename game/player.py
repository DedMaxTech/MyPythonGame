import pygame as pg
import math
from . import enemies, core, fx, level
from .UI import Interface, Button,ProgressBar
from . utils import *
from random import randint as rd

import cfg

PLAYER_IMG = pg.image.load('game/content/player2/player.png')
PLAYER_IMG_DEAD = pg.image.load('game/content/player2/player_dead.png')
PLAYER_LEGS_IDLE = pg.image.load('game/content/player2/legs/idle.png')
PLAYER_ARMS = pg.image.load('game/content/player2/arms.png')
PLAYER_LEGS_AIR = pg.image.load('game/content/player/legs/air.png')
PLAYER_LEGS_L = pg.image.load('game/content/player/legs/left.png')
PLAYER_LEGS_R = pg.image.load('game/content/player/legs/right.png')
BULLET_IMG = pg.image.load('game/content/player/guns/bullet.png')

PLAYER_ACCELERATION = 5
PLAYER_AIR_ACCELERATION = 3
PLAYER_MAX_SPEED = 5
JUMP_FORCE = 10
WALL_JUMP_FORCE = 6
GRAVITY = 0.4

RED_TINT = pg.Surface(PLAYER_IMG.get_size())
RED_TINT.fill('red')



sounds = not pg.mixer.get_init() is None
print('sound',sounds)
if sounds:
    print('load sound')
    SOUNDS = {
        'jump':pg.mixer.Sound('game/content/sounds/jump.wav'),
        'hurt':pg.mixer.Sound('game/content/sounds/hurt.wav'),
        'shoot':pg.mixer.Sound('game/content/sounds/shoot.wav'),
    }

GUNS = {
    'rifle': {'img': pg.image.load('game/content/player/guns/rifle.png'),
              'hold_img': 0,
              'pos': (29, 29),
              'bull_pos': (0, 0),
              'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
              'speed': 30,
              'mag': 30,
              'reload':2000,
              'dmg':15,
              'kd':100,
              'acc':2,
              'auto': True},
    'pistol': {'img': pg.image.load('game/content/player2/guns/pistol.png'),
               'hold_img': 0,
               'pos': (29, 29),
               'bull_pos': (0, 0),
               'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
               'speed': 30,
               'mag': 10,
               'reload': 1000,
               'dmg':35,
               'kd':300,
               'acc':1,
               'auto': False},
}


class Bullet(core.Actor):
    def __init__(self, x, y, xv,yv, img, rot, dmg, parent):
        w,h = img.get_size()
        super().__init__(x, y, w, h,gravity=0, friction=0)
        self.autodel(20)
        self.parent = parent
        self.damage = dmg
        self.img = pg.transform.rotate(img, abs(rot)).convert_alpha()
        self.xspeed, self.yspeed = xv,yv
        if xv < 0:
            self.img = pg.transform.flip(self.img,True,False)
        if yv > 0:
            self.img = pg.transform.flip(self.img,False,True)
        # self.trale = pg.Surface((20,20))
        # pg.draw.circle(self.trale,'yellow',(10,10),20)
        # self.trale.set_colorkey('black')

    def draw(self, screen: pg.Surface, camera):
        screen.blit(self.img, (self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h))
        # screen.blit(self.trale, real(self.rect.center, camera), special_flags=pg.BLEND_RGB_ADD)
        # screen.blit(self.img, self.rect.topleft, special_flags=pg.BLEND_RGB_ADD)
    def hit(self, actor):
        if actor == self.parent:
            return
        if isinstance(actor, enemies.BaseAI) and not isinstance(self.parent, enemies.BaseAI):
            actor.hp -= self.damage
            write_stat('done damage', get_stat('done damage')+self.damage)
            if not cfg.potato:
                fx.blood(self.rect.center,self.parent.world, int(self.damage*1.5/10))
                fx.damage(self.rect.center,-self.damage,self.parent.world)
            if sounds: SOUNDS['hurt'].play()
            if self.parent.aim_time < self.parent.AIM_TIME_MAX: self.parent.aim_time+=self.damage*10
            self._delete = True
        if isinstance(actor, Player):
            actor.hp -= self.damage
            write_stat('received damage', get_stat('received damage')+self.damage)
            actor.dmg_timer = 100
            self._delete = True
        if isinstance(actor, level.Block):
            if actor.type in [i for i in level.block_s if level.block_s[i]['dest']]: 
                actor.set_type('0')
            else:
                self._delete = True
            


class Player(core.Actor):
    AIM_TIME_MAX=5000
    def __init__(self, x, y, n=0, game_inst=None):
        super().__init__(x, y, 35,80, friction=0.2)
        self.n = n
        self.s = {}
        self.game = game_inst
        self.img = PLAYER_IMG
        self.ui = Interface(anims=False)

        self.move_left, self.move_right, self.jump, self.tp = False, False, False, False
        self.move_speed = 0
        self.look_r = True
        self.r_leg = True
        self.double = True
        self.aiming = False
        self.aim_time=self.AIM_TIME_MAX
        self.timer = 0
        self.angle = 0
        self.hp = 100
        self.dmg_timer = 0
        self.world = None
        self.shoot = False
        self.shoot_kd = 0
        self.inventory_kd = 1000
        self.font = pg.font.Font(cfg.font, 14)
        self.need_sides = True

        self.gun = 0
        self.guns = ['pistol', 'rifle']
        self.ammo = {'rifle': [30, 30], 'pistol': [10,50]}
        self._reload = False
        self.reload_kd = 0

        self.dead = False
        self.dead_kd = 2000

        self.ui.set_ui([
            ProgressBar((40,380), pg.image.load('game/content/ui/hp_full.png').convert_alpha(), pg.image.load('game/content/ui/hp_empty.png').convert_alpha(), colorkey='black'),
            ProgressBar((40,380), pg.image.load('game/content/ui/time_full.png').convert_alpha(), pg.image.load('game/content/ui/time_empty.png').convert_alpha(), colorkey='black'),
            Button((790,428),'yellow','', 20),
            Button((790,418),'red','', 15),
            Button((790,445),'white','', 15),
            Button((750,420),'white','',1,img='game/content/ui/ammo.png'),
            Button((20,422),'white','',1,img='game/content/ui/heart.png'),
            Button((30,410),'white','',1,img='game/content/ui/clock.png'),
        ])

    def process_move(self, d: dict):
        if d.get('right') is not None:
            self.move_right = d['right']
        if d.get('left') is not None:
            self.move_left = d['left']
        if d.get('up') is not None:
            self.jump = d['up']
        if d.get('look_r') is not None:
            self.look_r = d['look_r']
        if d.get('angle') is not None:
            self.angle = d['angle']
        if d.get('shoot') is not None:
            self.shoot = d['shoot']
        if d.get('tp') is not None:
            self.tp = d['tp']
        if d.get('wheel') is not None:
            self.gun += d['wheel']
            self.gun = self.gun % len(self.guns)
            self.inventory_kd = 1000
            self._reload = False
        if d.get('reload') is not None:
            self.reload()
        if d.get('aim') is not None:
            self.aiming = d['aim']

    def update_control(self,delta, blocks, level, tick=1):
        # HP MANAGEMENT
        if self.dead:
            return
        if self.hp <= 0: 
            self.dead=True
            self.autodel(3)
            self.game.death()
        
        #UI UPDATE
        amm = self.ammo[self.guns[self.gun]]
        self.ui.buttons[0].value = self.hp/100
        self.ui.buttons[1].value = remap(self.aim_time, (0, self.AIM_TIME_MAX))
        self.ui.buttons[2].text = f'{amm[0]}/{amm[1]}'

        

        if self.reload_kd>0 and self._reload:
            self.ui.buttons[3].text = f'{self.reload_kd/1000:.2f}'
        else:
            self.ui.buttons[3].text = ''
        self.ui.buttons[4].text = self.guns[self.gun].title()

        # TIMERS
        if self.dmg_timer >0: self.dmg_timer-=delta
        if self.shoot_kd >0: self.shoot_kd -= delta
        if self.inventory_kd>0: self.inventory_kd -= delta
        if not self.aiming and self.aim_time<self.AIM_TIME_MAX: self.aim_time += delta/30

        # RELOAD
        if self._reload:
            if self.reload_kd>0: self.reload_kd -= delta
            else:
                amm = self.ammo[self.guns[self.gun]]
                if amm[1]>0:
                    m = GUNS[self.guns[self.gun]]['mag']
                    for i in range(1,m+1):
                        if amm[1]-i<=0: 
                            m=i
                            break
                    self.ammo[self.guns[self.gun]] = [m, self.ammo[self.guns[self.gun]][1]-m]
                self._reload = False

        if self.on_ground:
            self.double = True
        self.world = level

        # SIDE MOVE
        ACCEL = PLAYER_ACCELERATION
        if self.move_right and not self.right: self.xspeed += ACCEL -self.xspeed
        if self.move_left and not self.left: self.xspeed -= ACCEL+self.xspeed

        #AIM
        if self.aiming:
            if self.aim_time<=0:self.aiming=False
            else:   self.aim_time-=delta

        # TELEPORT ABIL.
        if self.tp:
            self.tp = False
            # self.rect.center = self.get_point(level, 200)
            xv, yv = vec_to_speed(15, -self.angle)
            self.xspeed += xv if self.look_r else -xv
            self.yspeed = yv

        # JUMP
        self._jump(tick)

        # SHOOT
        if self.shoot and self.shoot_kd<=0: self._shoot()

    def _jump(self, tick):
        if self.jump:
            # if not self.on_ground and self.double:
            #     self.double = False
                # self.xspeed = 0
            if not self.on_ground:
                if self.left and self.move_left and self.look_r:
                    self.move_left = False
                    self.xspeed += WALL_JUMP_FORCE+WALL_JUMP_FORCE*abs(1-tick)
                    self.double = True
                elif self.right and self.move_right and not self.look_r:
                    self.move_right = False
                    self.xspeed -= WALL_JUMP_FORCE+WALL_JUMP_FORCE*abs(1-tick)
                    self.double = True
                elif self.double: self.double = False
                else:return
            self.jump = False
            self.yspeed = -(JUMP_FORCE+JUMP_FORCE*abs(1-tick)) 
            self.on_ground = False
            if sounds: SOUNDS['jump'].play()
    def reload(self):
        self._reload = True
        self.ammo[self.guns[self.gun]] = [0, self.ammo[self.guns[self.gun]][0]+self.ammo[self.guns[self.gun]][1]]
        self.reload_kd = GUNS[self.guns[self.gun]]['reload']

    def _shoot(self):
        if self._reload: 
            self.shoot = False
            return
        if self.ammo[self.guns[self.gun]][0]<=0:
            self.shoot = False
            self.reload()
            return
        gun = GUNS[self.guns[self.gun]]
        acc = gun['acc'] if self.aiming else gun['acc']*2
        xvel, yvel = vec_to_speed(gun['speed'], self.angle+(rd(-acc*5, acc*5)/3))
        d = gun['dmg']
        b = Bullet(self.rect.x + gun['pos'][0],
                  self.rect.y + gun['pos'][1],
                  xvel if self.look_r else -xvel,
                  -yvel,
                  gun['bull_img'], self.angle,rd(int(d-(d*0.2)), int(d+(d*0.2))), self
        )
        self.game.world.actors.append(b)

        self.ammo[self.guns[self.gun]][0] -= 1

        if self.shoot and self.game: self.game.shake = 5

        self.shoot_kd = gun['kd']
        self.shoot = gun['auto']
        if sounds: SOUNDS['shoot'].play()
        write_stat('shoots', get_stat('shoots')+1)

    def get_point(self, world, rad, ang=None):
        r = rad
        rect = self.rect.copy()
        while r>=0:
            rect.center = self.rect.center
            angle = rd(-180, 0) if ang is None else ang
            x, y = vec_to_speed(r, angle)
            rect.x += x; rect.y+=y
            if not world.get_blocks(rect):
                return rect.center
            r-=1
        return self.rect.center

    def rotate(self):
        self.img = pg.transform.flip(self.img, True, False)

    def draw(self, screen: pg.Surface, camera: pg.Rect):
        self.img = PLAYER_IMG.copy()
        # if self.on_ground:
        #     if self.xspeed == 0:
        #         self.img.blit(PLAYER_LEGS_IDLE, (0, 53))
        #     else:
        #         self.img.blit(PLAYER_LEGS_R if self.r_leg else PLAYER_LEGS_L, (0, 53))
        # else:
        #     self.img.blit(PLAYER_LEGS_AIR, (0, 53))
        # self.img.blit(PLAYER_LEGS_AIR, (0, 0))
        off = 0 if self.look_r else -30
        offy = 0 if not self.aiming else -7
        if not self.on_ground and ((self.left and self.move_left and self.look_r) or (self.right and self.move_right and not self.look_r)):
            self.img = pg.transform.rotate(self.img, -30)
            off = -10 if self.look_r else -60
        gun_img = pg.transform.rotate(GUNS[self.guns[self.gun]]['img'].copy(), self.angle)
        # debug(gun_img.get_rect().center, screen)
        self.img.blit(gun_img, (gun_img.get_rect().x+20, gun_img.get_rect().y+37+offy))
        # if not self.look_r and self.xspeed > 0: self.rotate()
        # if self.look_r and self.xspeed < 0: self.rotate()
        if self.dead: self.img = PLAYER_IMG_DEAD
        if not self.look_r: self.rotate()
        if not self.dead:
            if self.dmg_timer > 0: self.img.blit(RED_TINT,(0,0),special_flags=pg.BLEND_RGB_ADD)
            if self.inventory_kd>0:self.img.blit(self.font.render(f'[{self.guns[self.gun]}]',False,'white'), (-off,0))
        # screen.fill('green',(self.pre_rect.x - camera.x, self.pre_rect.y + camera.y, self.pre_rect.w, self.pre_rect.h))
        
        screen.blit(self.img,
                    (self.rect.x - camera.x+off, self.rect.y - camera.y))
        self.ui.draw(self.game.screen)
