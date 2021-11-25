import pygame as pg
import math
from . import enemies, core, fx, level
from .UI import Interface, Button,ProgressBar
from . utils import *
from random import randint as rd
import cfg

IMGS = {
    'PLAYER':pg.image.load('game/content/player2/player.png'),
    'BACK':pg.image.load('game/content/player2/back.png'),
    'GRENADE':pg.image.load('game/content/player2/guns/grenade.png')
}

PLAYER_IMG = pg.image.load('game/content/player2/player.png')
BACK_IMG = pg.image.load('game/content/player2/back.png')
PLAYER_IMG_DEAD = pg.image.load('game/content/player2/player_dead.png')
PLAYER_LEGS_IDLE = pg.image.load('game/content/player2/legs/idle.png')
PLAYER_ARMS = pg.image.load('game/content/player2/arms.png')
PLAYER_LEGS_AIR = pg.image.load('game/content/player/legs/air.png')
PLAYER_LEGS_L = pg.image.load('game/content/player/legs/left.png')
PLAYER_LEGS_R = pg.image.load('game/content/player/legs/right.png')
BULLET_IMG = pg.image.load('game/content/player/guns/bullet.png')

# parts
PART_BACK = pg.image.load('game/content/player2/died/back.png')
PART_HEAD = pg.image.load('game/content/player2/died/head.png')
PART_LEGS = pg.image.load('game/content/player2/died/legs.png')

PLAYER_ACCELERATION = 5
PLAYER_AIR_ACCELERATION = 3
PLAYER_MAX_SPEED = 5
JUMP_FORCE = 10
WALL_JUMP_FORCE = 6
GRAVITY = 0.4

RED_TINT = pg.Surface(PLAYER_IMG.get_size())
RED_TINT.fill('red')




sounds = not pg.mixer.get_init() is None
# print('sound',sounds)
if sounds:
    print('load sound')
    SOUNDS = {
        'jump':pg.mixer.Sound('game/content/sounds/jump.wav'),
        'hurt':pg.mixer.Sound('game/content/sounds/hurt.wav'),
        'shoot':pg.mixer.Sound('game/content/sounds/shoot.wav'),
        'expl':pg.mixer.Sound('game/content/sounds/explosion.wav'),
    }

GUNS = {
    'rifle': {'img': pg.image.load('game/content/player/guns/rifle.png'),
              'hold_img': 0,
              'pos': (29, 29),
              'offy':0,
              'bull_pos': (0, 0),
              'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
              'speed': 20,
              'mag': 30,
              'amount': 1,
              'reload':1500,
              'dmg':15,
              'kd':100,
              'acc':2,
              'auto': True,
              'shake':7,
              'back':1},
    'pistol': {'img': pg.image.load('game/content/player2/guns/pistol.png'),
               'hold_img': 0,
               'pos': (29, 29),
               'offy':0,
               'bull_pos': (0, 0),
               'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
               'speed': 25,
               'mag': 10,
               'amount': 1,
               'reload': 1000,
               'dmg':35,
               'kd':300,
               'acc':1,
               'auto': False,
               'shake':9,
               'back':3},
    'shootgun': {'img': pg.image.load('game/content/player2/guns/shootgun.png'),
            'hold_img': 0,
            'pos': (29, 29),
            'offy':-5,
            'bull_pos': (0, 0),
            'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
            'speed': 25,
            'mag': 5,
            'amount': 3,
            'reload': 3000,
            'dmg':20,
            'kd':500,
            'acc':1,
            'auto': False,
            'shake':15,
            'back':10},
    'minigun': {'img': pg.image.load('game/content/player2/guns/minigun.png'),
            'hold_img': 0,
            'pos': (29, 29),
            'offy':-5,
            'bull_pos': (0, 0),
            'bull_img':pg.image.load('game/content/player/guns/bullet.png'),
            'speed': 25,
            'mag': 100,
            'amount': 1,
            'reload': 3000,
            'dmg':7,
            'kd':50,
            'acc':1,
            'auto': True,
            'shake':7,
            'back':1},
}

def convert():
    for key, val in IMGS.items():
        IMGS[key] = val.convert_alpha()
    for d in GUNS.values():
        d['img'] = d['img'].convert_alpha()
        d['bull_img'] = d['bull_img'].convert_alpha()
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
        self.ignore_tmr = 200
        self.pre_rect = pg.Rect(x-50,y-50,w+50,h+50)
        # self.trale = pg.Surface((20,20))
        # pg.draw.circle(self.trale,'yellow',(10,10),20)
        # self.trale.set_colorkey('black')

    def update(self, delta, blocks, actors):
        if self.ignore_tmr>0: self.ignore_tmr-=delta
        return super().update(delta, blocks, actors)
    
    def draw(self, screen: pg.Surface, camera):
        screen.blit(self.img, (self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h))
        # screen.blit(self.trale, real(self.rect.center, camera), special_flags=pg.BLEND_RGB_ADD)
        # screen.blit(self.img, self.rect.topleft, special_flags=pg.BLEND_RGB_ADD)
    def hit(self, actor):
        if actor == self.parent and self.ignore_tmr>0:
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
                # actor.set_type('0')
                actor.delete()
                self.delete()
            else:
                self._delete = True
            
class Grenade(core.Actor):
    def __init__(self, x, y, xv,yv, world):
        super().__init__(x, y, 9,11, bounce=0.3, friction=0.1,image=IMGS['GRENADE'])
        self.xspeed, self.yspeed = xv,yv
        self.explose_tmr = 3500
        self.world =world
        r=120
        self.pre_rect = pg.Rect(x-r,y-r, r*2,r*2)
        
    def update(self, delta, blocks, actors):
        self.explose_tmr-=delta
        if self.explose_tmr<=0: self.explose(blocks,actors)
        return super().update(delta, blocks, actors)
    
    def explose(self,blocks, actors):
        r = 200
        dest = [key for key, val in level.block_s.items() if val['dest']]
        for a in actors+blocks:
            if isinstance(a, core.Actor):
                d = distanse(self.rect.center, a.rect.center)
                if d<r:
                    dmg=int(remap(r-d, (0,r), (20,120)))
                    xv,yv = vec_to_speed(dmg/5, 180-angle(a.rect.center,self.rect.center,))
                    a.xspeed, a.yspeed = xv if self.rect.x>a.rect.x else -xv,(yv if self.rect.x>a.rect.x else -yv)-1 
                    if isinstance(a, Player) or isinstance(a, enemies.BaseAI):
                        a.hp -= dmg
                        if not cfg.potato: fx.damage(a.rect.center, dmg, self.world)
            if isinstance(a, level.Block) and a.type in dest:
                a.delete()
        if sounds: SOUNDS['expl'].play()
        if not cfg.potato: fx.explosion(self.rect.center,self.world, 30)
        self.delete()
        

class Player(core.Actor):
    AIM_TIME_MAX=5000
    def __init__(self, x, y, n=0, game_inst=None):
        super().__init__(x, y, 35,63, friction=0.2)
        self.n = n
        self.s = {}
        self.game = game_inst
        self.img = PLAYER_IMG
        self.ui = Interface(anims=False)
        convert()
        
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
        self.max_hp = 100
        self.dmg_timer = 0
        self.world = None
        self.shoot = False
        self.shoot_kd = 0
        self.inventory_kd = 1000
        self.font = pg.font.Font(cfg.font, 14)
        self.need_sides = True
        self.to_ang=0

        self.gun = 0
        self.guns = ['pistol']
        self.ammo = {'rifle': [30, 30], 'pistol': [10,50],'shootgun':[5,10], 'minigun':[100,200]}
        self.grenades = 40
        self.grenade=False
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
            Button((760,460),'white','', 15),
            Button((750,420),'white','',1,img='game/content/ui/ammo.png'),
            Button((20,422),'white','',1,img='game/content/ui/heart.png'),
            Button((30,410),'white','',1,img='game/content/ui/clock.png'),
            Button((750,463),'white','',1,img='game/content/ui/grenade.png'),
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
        if d.get('grenade') is not None:
            self.grenade = d['grenade']
        if d.get('wheel') is not None:
            self.gun += d['wheel']
            self.gun = self.gun % len(self.guns)
            self.inventory_kd = 1000
            self._reload = False
        if d.get('reload') is not None:
            self.reload()
        if d.get('aim') is not None:
            self.aiming = d['aim']


    def death(self):
        self.dead=True
        self.autodel(3)
        self.game.death()
        prts = [
            core.Actor(self.rect.centerx, self.rect.centery, 40,30,0.5,friction=0.1, image=PART_BACK),
            core.Actor(self.rect.centerx, self.rect.centery, 40,30,0.5,friction=0.1, image=PART_HEAD),
            core.Actor(self.rect.centerx, self.rect.centery, 40,30,0.5,friction=0.1, image=PART_LEGS),
        ]
        for i in prts:
            i.xspeed = self.xspeed+rd(-3,3)
            i.yspeed = self.yspeed-5
        self.game.world.actors += prts
        fx.blood(self.rect.center, self.game.world, 50)
    def update_control(self,delta, blocks, level, tick=1):
        # HP MANAGEMENT
        # UI
        self.ui.update_buttons()
        
        if self.dead:
            return
        if self.hp <= 0: 
            self.death()
        
        #UI UPDATE
        amm = self.ammo[self.guns[self.gun]]
        self.ui.buttons[0].value = self.hp/100
        self.ui.buttons[1].value = remap(self.aim_time, (0, self.AIM_TIME_MAX))
        self.ui.buttons[2].text = f'{amm[0]}/{amm[1]}'
        self.ui.buttons[5].text = str(self.grenades)

        

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
            if self.reload_kd>0: 
                self.reload_kd -= delta
                self.to_ang = remap(self.reload_kd, (0, GUNS[self.guns[self.gun]]['reload']/GUNS[self.guns[self.gun]]['amount']), (0,360))
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
        else:self.to_ang=0

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
        
        # grenades
        if self.grenade: self.throw_genade()
        

    def _jump(self, tick):
        if self.jump:
            # if not self.on_ground and self.double:
            #     self.double = False
                # self.xspeed = 0
            if not self.on_ground:
                if self.left and self.move_left and self.look_r:
                    self.move_left = False
                    self.xspeed += WALL_JUMP_FORCE
                    self.double = True
                elif self.right and self.move_right and not self.look_r:
                    self.move_right = False
                    self.xspeed -= WALL_JUMP_FORCE
                    self.double = True
                elif self.double: self.double = False
                else:return
            self.jump = False
            self.yspeed = -JUMP_FORCE
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
        for i in range(gun['amount']):
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
        xv,yv=vec_to_speed(gun['back'], self.angle-180)
        self.xspeed, self.yspeed = self.xspeed+(xv if self.look_r else-xv), self.yspeed-yv
        if self.shoot and self.game: self.game.shake = gun['shake']

        self.shoot_kd = gun['kd']
        self.shoot = gun['auto']
        if sounds: SOUNDS['shoot'].play()
        write_stat('shoots', get_stat('shoots')+1)
    
    def throw_genade(self):
        self.grenade=False
        if self.grenades<=0: return
        self.grenades-=1
        xv,yv = vec_to_speed(20 if self.aiming else 15, self.angle)
        self.game.world.actors.append(Grenade(self.rect.centerx,self.rect.y+10,xv if self.look_r else -xv, -yv, self.game.world))
        

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
        self.img = IMGS['BACK'].copy()
        self.img.blit(IMGS['PLAYER'].copy(), (0,0))
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
            off = 0 if self.look_r else -60
        gun_img = pg.transform.rotate(GUNS[self.guns[self.gun]]['img'].copy(), self.angle-self.to_ang)
        # debug(gun_img.get_rect().center, screen)
        w,h=gun_img.get_width()/2,gun_img.get_height()/2
        self.img.blit(gun_img, (gun_img.get_rect().x+30-w, gun_img.get_rect().y+35+offy+GUNS[self.guns[self.gun]]['offy']-h))
        # if not self.look_r and self.xspeed > 0: self.rotate()
        # if self.look_r and self.xspeed < 0: self.rotate()
        if self.dead: self.img = PLAYER_IMG_DEAD
        if not self.look_r: self.rotate()
        if not self.dead:
            if self.dmg_timer > 0: self.img.blit(RED_TINT,(0,0),special_flags=pg.BLEND_RGB_ADD)
            # if self.inventory_kd>0:self.img.blit(self.font.render(f'[{self.guns[self.gun]}]',False,'white'), (-off,0))
        # screen.fill('green',(self.pre_rect.x - camera.x, self.pre_rect.y + camera.y, self.pre_rect.w, self.pre_rect.h))
        
        if not self.dead:
            screen.blit(self.img, (self.rect.x - camera.x+off-3, self.rect.y - camera.y))
        self.ui.draw(self.game.screen)
