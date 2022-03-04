import pygame as pg
import math
from . import enemies, core, fx, level, objects, weapons
from .UI import HBox, Interface, Button,ProgressBar, VBox, RIGHT,LEFT,FILL,DOWN,UP
from . utils import *
from random import randint as rd
import cfg

IMGS = {
    'PLAYER':pg.image.load('game/content/player2/player.png'),
    'BACK':pg.image.load('game/content/player2/back.png'),
    'GRENADE':pg.image.load('game/content/player2/guns/grenade.png')
}
IMGS2 = {
    'CENTER':pg.image.load('game/content/slime2/center.png'),
    'DOWN':pg.image.load('game/content/slime2/down.png'),
    'DOWNLEFT':pg.image.load('game/content/slime2/downleft.png'),
    'LEFT':pg.image.load('game/content/slime2/left.png'),
    'DOWNBOTH':pg.image.load('game/content/slime2/downboth.png'),
    'DOWNBOTH':pg.image.load('game/content/slime2/downboth.png'),
    'UPDOWN':pg.image.load('game/content/slime2/updown.png'),
    'UPDOWNLEFT':pg.image.load('game/content/slime2/updownleft.png'),
    'FACE':pg.image.load('game/content/slime2/face.png'),
    'SHADOW':pg.image.load('game/content/slime2/shadow.png'),
    'ALPHA':pg.Surface((70,70),flags= pg.SRCALPHA),
}

# alpha_sf = pg.Surface(IMGS2['CENTER'].get_size(),24, pg.SRCALPHA)


IMGS2['DOWNRIGHT'] = pg.transform.flip(IMGS2['DOWNLEFT'], True, False)
IMGS2['RIGHT'] = pg.transform.flip(IMGS2['LEFT'], True, False)
IMGS2['UP'] = pg.transform.flip(IMGS2['DOWN'], False, True)
IMGS2['UPLEFT'] = pg.transform.flip(IMGS2['DOWNLEFT'], False, True)
IMGS2['UPRIGHT'] = pg.transform.flip(IMGS2['DOWNRIGHT'], False, True)
IMGS2['UPBOTH'] = pg.transform.flip(IMGS2['DOWNBOTH'], False, True)
IMGS2['UPDOWNRIGHT'] = pg.transform.flip(IMGS2['UPDOWNLEFT'], True, False)

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
    SOUNDS = {
        'jump':pg.mixer.Sound('game/content/sounds/jump.wav'),
        'hurt':pg.mixer.Sound('game/content/sounds/hurt.wav'),
        'shoot':pg.mixer.Sound('game/content/sounds/shoot.wav'),
        'expl':pg.mixer.Sound('game/content/sounds/explosion.wav'),
    }

def convert():
    for key, val in IMGS2.items():
        IMGS2[key] = val.convert_alpha()
    for d in weapons.GUNS.values():
        d['img'] = d['img'].convert_alpha()
        d['bull_img'] = d['bull_img'].convert_alpha()

def change_color(color):
    s = pg.Surface(IMGS2['CENTER'].get_size())
    s.fill(color)
    for k in IMGS2.keys():
        IMGS2[k].blit(s, (0,0), special_flags=pg.BLEND_RGBA_MULT)

change_color((50,202,43))

class Grenade(core.Actor):
    def __init__(self, x, y, xv,yv, game):
        super().__init__(x, y, 9,11, bounce=0.45, friction=0.1,image=IMGS['GRENADE'])
        self.speed = Vec(xv,yv)
        self.explose_tmr = 3500
        self.game =game
        r=120
        self.pre_rect = pg.Rect(x-r,y-r, r*2,r*2)
        
    def update(self, delta, blocks, actors):
        self.explose_tmr-=delta
        if self.explose_tmr<=0: self.explose(blocks,actors)
        return super().update(delta, blocks, actors)
    
    def explose(self,blocks, actors):
        r = 230
        dest = [key for key, val in level.block_s.items() if val['dest']]
        for a in actors+blocks:
            if isinstance(a, core.Actor):
                d = distanse(self.rect.center, a.rect.center)
                if d<r:
                    dmg=int(remap(r-d, (0,r), (20,120)))
                    xv,yv = vec_to_speed(dmg/5, 180-angle(a.rect.center,self.rect.center,))
                    a.speed.xy = -xv, -yv
                    a.on_fire = rd(5000,8000)
                    if isinstance(a, Player) or isinstance(a, enemies.BaseAI):
                        self.game.stats['done damage']+=dmg
                        a.hp -= dmg
                        if not cfg.potato: fx.damage(a.rect.center, dmg, self.game.world)
            if isinstance(a, level.Block) and a.type in dest:
                a.delete()
        self.game.shake=20
        if sounds: SOUNDS['expl'].play()
        if not cfg.potato: fx.explosion(self.rect.center,self.game.world, 30)
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
        self.hp = 200
        self.max_hp = 200
        self.dmg_timer = 0
        self.world = None
        self.shoot = False
        self.shoot_kd = 0
        self.inventory_kd = 1000
        self.font = pg.font.Font(cfg.font, 14)
        self.need_sides = True
        self.to_ang=0
        self.recoil=0
        self.wall_jump_kd = 0
        self.m_coords = (0,0)

        self.anim_timer = 0
        self.anim_flag = False


        self.up = False
        self.gun = 0
        self.guns = ['pistol']
        self.ammo = {'rifle': [30, 60], 'pistol': [10,50],'shootgun':[5,15], 'minigun':[100,100], 'sniper':[5,15]}
        self.grenades = 40
        self.grenade=False
        self._reload = False
        self.reload_kd = 0

        self._hook = False
        self.hook_point = Vec(0,0)
        self.hook_frames = 0
        self.hook_ang = 0
        
        self.bonus = {
            'Double gun':0,
            'Armor':0,
            'Time stop':0,
        }

        self.flashlight = objects.PointLight(*self.rect.center)
        self.self_light = objects.Light(*self.rect.center, scale=1.2)

        self.dead = False
        self.dead_kd = 2000

        self.event_ui = VBox(0,(700,0), (154,400), anchor_h=RIGHT, anchor_v=DOWN)
        self.hp_bar= ProgressBar((40,380), pg.image.load('game/content/ui/hp_full.png').convert_alpha(), pg.image.load('game/content/ui/hp_empty.png').convert_alpha(), colorkey='black')
        self.time_bar = ProgressBar((40,380), pg.image.load('game/content/ui/time_full.png').convert_alpha(), pg.image.load('game/content/ui/time_empty.png').convert_alpha(), colorkey='black')
        self.ammo_but = Button((790,428),'yellow','', 20)
        self.reload_but = Button((790,418),'red','', 15)
        self.gun_but = Button((790,445),'white','', 15)
        self.grenades_but = Button((760,460),'white','', 15)
        self.ui.set_ui([
            self.hp_bar,
            self.time_bar,
            self.ammo_but,
            self.reload_but,
            self.gun_but,
            self.grenades_but,
            self.event_ui,
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
        # if d.get('look_r') is not None:
        #     self.look_r = d['look_r']
        # if d.get('angle') is not None:
        #     self.angle = d['angle']
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
        if d.get('coords') is not None:
            self.m_coords = d['coords']
        if d.get('hook') is not None:
            self.hook_frames = 0
            if self._hook and not d['hook']:
                if not self.on_ground:
                    if self.right: 
                        self.speed.x-=WALL_JUMP_FORCE
                        self.speed.y -= JUMP_FORCE
                    if self.left: 
                        self.speed.x+=WALL_JUMP_FORCE
                        self.speed.y -= JUMP_FORCE
                    if not self.up: self.wall_jump_kd = 500
            self._hook = False
            if not self._hook and d['hook']:
                _, self.hook_point.xy, _ = self.game.world.raycast(self.rect.center, (-self.angle if self.look_r else self.angle+180), 700,self.game.camera)
                bl = self.game.world.get_blocks(pg.Rect(self.hook_point-(1,1),(2,2)))
                self._hook = not not bl
            if not self._hook: self.hook_ang =0 
        


    def to_death(self):
        self.dead=True
        self.autodel(3)
        self.game.death()

        fx.slimes(self.rect.center, self.game.world, 12,50)
        # prts = [
        #     core.Actor(self.rect.centerx, self.rect.centery, 40,30,0.5,friction=0.1, image=PART_BACK),
        #     core.Actor(self.rect.centerx, self.rect.centery, 40,30,0.5,friction=0.1, image=PART_HEAD),
        #     core.Actor(self.rect.centerx, self.rect.centery, 40,30,0.5,friction=0.1, image=PART_LEGS),
        # ]
        # for i in prts:
        #     i.speed.xy = self.speed.x+rd(-3,3),self.speed.y-5
        #     # i.xspeed = self.xspeed+rd(-3,3)
        #     # i.yspeed = self.yspeed-5
        # self.game.world.actors += prts
        # fx.blood(self.rect.center, self.game.world, 50)
        

    def update_control(self,delta, blocks, level, tick=1):
        # HP MANAGEMENT
        # UI
        self.ui.update(delta=delta)
        if self.dead and self.die_kd<1500:self.game.v=0
        if self.dead:
            return
        # if self.hp <= 0: 
        #     self.death()
        if self.hp<=0: self.to_death()
        if self.ammo.get(self.guns[self.gun]) is None: self.ammo[self.guns[self.gun]]=[0,0]

        #UI UPDATE
        amm = self.ammo[self.guns[self.gun]]
        self.hp_bar.value = remap(self.hp, (0,self.max_hp))
        self.time_bar.value = remap(self.aim_time, (0, self.AIM_TIME_MAX))
        self.ammo_but.text = f'{amm[0]}/{amm[1]}'
        self.grenades_but.text = str(self.grenades)
        for w in self.event_ui.widgets:
            for k, v in self.bonus.items():
                if w.text.startswith(k):
                    if v>0:w.text = f'{k}: {v/1000:.1f}'
                    else: w.delete()

        if self.reload_kd>0 and self._reload:
            self.reload_but.text = f'{self.reload_kd/1000:.2f}'
        else:
            self.reload_but.text = ''
        self.gun_but.text = self.guns[self.gun].title()

        # TIMERS
        if self.anim_timer >0: self.anim_timer-=delta
        else:
            self.anim_timer=200
            self.anim_flag = not self.anim_flag
        if self.dmg_timer >0: self.dmg_timer-=delta
        if self.shoot_kd >0: self.shoot_kd -= delta
        if self.inventory_kd>0: self.inventory_kd -= delta
        if not self.aiming and self.aim_time<self.AIM_TIME_MAX: self.aim_time += delta/30
        if self.wall_jump_kd>0: self.wall_jump_kd-=delta
        for k,v in self.bonus.items():
            if v>0: self.bonus[k]-=delta


        self.up = self.check_up(blocks)

        # ANGLE AND LOOK DIRECTION
        if self.on_ground and self.speed.x:
            fx.slimes((rd(self.rect.left,self.rect.right), self.rect.bottom), self.game.world,2,amount=1)

        x,y = self.m_coords
        w,h = self.game.frame.get_size()
        x,y = remap(x, (0, cfg.screen_h), (0,w)), remap(y, (0, cfg.screen_v), (0,h))
        x, y =x+self.game.camera.x - self.rect.centerx-42, y + self.game.camera.y - self.rect.centery-40

        self.look_r = x>=0
        self.angle = angle((abs(x),y))

        if self.on_ground: self.wall_jump_kd=0
        # x,y = self.m_coords
        # w,h = self.game.frame.get_size()
        # x,y = remap(x, (0, cfg.screen_h), (0,w)), remap(y, (0, cfg.screen_v), (0,h))
        # # x, y =x+self.game.camera.x - self.rect.centerx, self.rect.centery - y - self.game.camera.y
        
        # self.look_r = x>=0
        # self.angle = angle(self.rect.center, (self.game.camera.x+x,))

        # RELOAD
        if self._reload:
            if self.reload_kd>0: 
                self.reload_kd -= delta
                self.to_ang = remap(self.reload_kd, (0, weapons.GUNS[self.guns[self.gun]]['reload']/weapons.GUNS[self.guns[self.gun]]['amount']), (0,360))
            else:
                amm = self.ammo[self.guns[self.gun]]
                if amm[1]>0:
                    m = weapons.GUNS[self.guns[self.gun]]['mag']
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
        if self.move_right and not self.right: self.speed.x += ACCEL -self.speed.x
        if self.move_left and not self.left: self.speed.x -= ACCEL+self.speed.x

        #AIM
        if self.aiming:
            if self.aim_time<=0:self.aiming=False
            else:   self.aim_time-=delta

        # TELEPORT ABIL.
        if self.tp:
            self.tp = False
            # self.rect.center = self.get_point(level, 200)
            xv, yv = vec_to_speed(15, -self.angle)
            self.speed.x += xv if self.look_r else -xv
            self.speed.y = yv

        self.game.world.neo_mode = self.bonus['Time stop']>0
        
        # JUMP
        self._jump()
        if not self.on_ground and 450>self.wall_jump_kd>0 and (self.right or self.left): self.wall_jump_kd = 0

        # SHOOT
        if self.shoot and self.shoot_kd<=0: self._shoot()
        
        # grenades
        if self.grenade: self.throw_genade()
        
        if self.game and self.on_fire>0: fx.fire(self.rect.center,self.game.world,6)

        # LIGHT
        self.flashlight.rect.topleft = self.rect.center
        self.flashlight.rot = (-self.angle if self.look_r else self.angle+180)-90
        self.flashlight.reset()

        self.self_light.rect.topleft = self.rect.center

        # HOOK
        if self._hook: self.hook(level)
    
    def damage(self, hp):
        if self.bonus['Armor']: hp/=4
        self.hp -= hp
        self.damaged(hp)
    
    def hook(self, world):
        ang = angle(self.hook_point.xy,self.rect.center)
        self.hook_ang = ang
        self.speed.xy = self.speed * 0.95 + vec_to_speed(1.3, -ang) # (-self.angle if self.look_r else self.angle+180)
        
    def _jump(self):
        if self.jump:
            # if not self.on_ground and self.double:
            #     self.double = False
                # self.xspeed = 0
            if not self.on_ground:
                if self.left and self.move_left and self.look_r:
                    self.wall_jump_kd=500
                    self.move_left = False
                    self.speed.x += WALL_JUMP_FORCE
                    self.double = True
                elif self.right and self.move_right and not self.look_r:
                    self.wall_jump_kd=500
                    self.move_right = False
                    self.speed.x -= WALL_JUMP_FORCE
                    self.double = True
                elif self.double:
                    # fx.fire((self.rect.centerx,self.rect.bottom),self.game.world,20)
                    fx.slimes(self.rect.center, self.game.world)
                    self.double = False
                else:return
            self.jump = False
            self.speed.y = -JUMP_FORCE
            self.on_ground = False
            if sounds: SOUNDS['jump'].play()

    def reload(self):
        self._reload = True
        self.ammo[self.guns[self.gun]] = [0, self.ammo[self.guns[self.gun]][0]+self.ammo[self.guns[self.gun]][1]]
        self.reload_kd = weapons.GUNS[self.guns[self.gun]]['reload']

    def _shoot(self):
        if self._reload: 
            self.shoot = False
            return
        if self.ammo[self.guns[self.gun]][0]<=0:
            self.shoot = False
            self.reload()
            return
        gun = weapons.GUNS[self.guns[self.gun]]
        acc = gun['acc'] if self.aiming else gun['acc']*2
        for i in range(gun['amount'] if not self.bonus['Double gun']>0 else gun['amount']*2):
            xvel, yvel = vec_to_speed(gun['speed'], self.angle+(rd(-acc*5, acc*5)/3))
            d = gun['dmg']
            # b = Bullet(self.rect.centerx,
            #         self.rect.centery,
            #         xvel if self.look_r else -xvel,
            #         -yvel,
            #         gun['bull_img'], self.angle,rd(int(d-(d*0.2)), int(d+(d*0.2))), self
            # )
            b = gun['bullet'](*self.rect.center,
                            xv=(xvel if self.look_r else -xvel),
                            yv=-yvel,
                            img = gun['bull_img'],
                            rot = self.angle,
                            dmg=rd(int(d-(d*0.2)), int(d+(d*0.2))),
                            parent = self)
            self.game.world.actors.append(b)

        self.ammo[self.guns[self.gun]][0] -= 1
        xv,yv=vec_to_speed(gun['back'] if not self.bonus['Double gun']>0 else gun['back']*2, self.angle-180)
        self.speed.x, self.speed.y = self.speed.x+(xv if self.look_r else-xv), self.speed.y-yv
        if self.shoot and self.game: self.game.shake = gun['shake']

        self.recoil=gun['recoil']
        self.shoot_kd = gun['kd']
        self.shoot = gun['auto']
        if sounds: SOUNDS['shoot'].play()
        self.game.stats['shoots']+=1
        # write_stat('shoots', get_stat('shoots')+1)
        if self.ammo[self.guns[self.gun]][0] == 0: self.reload()
    
    def land(self, speed):
        fx.slimes(self.rect.center, self.game.world)
        # if self._hook: 
        #     self.speed.y = -abs(speed.y)*3
        #     self._hook = False
        #     self.on_ground=False

    def throw_genade(self):
        self.grenade=False
        if self.grenades<=0: return
        self.grenades-=1
        xv,yv = vec_to_speed(20 if self.aiming else 15, self.angle)
        self.game.world.actors.append(Grenade(self.rect.centerx,self.rect.y+10,xv if self.look_r else -xv, -yv, self.game))
    
    # def hit(self, actor):
    #     if isinstance(actor,level.Block):
    #         fx.slimes((self.rect.centerx, self.rect.bottom), self.game.world,2,amount=1)
    #     return super().hit(actor)

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

    def rotate(self):
        self.img = pg.transform.flip(self.img, True, False)
        
    def debug_draw(self, screen, camera):
        pg.draw.rect(screen, 'red', real(pg.Rect(self.hook_point[0]-2,self.hook_point[1]-2,4,4), camera))
        if not self._hook: pg.draw.line(screen,'yellow', real(self.rect.center, camera), real(self.hook_point, camera))
        return super().debug_draw(screen, camera)
    
    def light_draw(self, screen: pg.Surface, camera: pg.Rect):
        # self.flashlight.light_draw(screen,camera)
        if not cfg.allow_c:self.flashlight.light_draw(screen,camera)
        else:
            # Ray cast light
            # ps = [real(self.rect.center,camera)]
            # for i in range(10):
            #     _, p, _ = self.game.world.raycast(self.rect.center, (-self.angle if self.look_r else self.angle+180)+ i*4 - 10,500, camera=camera)
            #     ps.append(real(p,camera))
            ps = [real(self.rect.center,camera), *[real(p,camera) for p in self.game.world.multi_ray_cast(self.rect.center, [(-self.angle if self.look_r else self.angle+180)+ i*4 - 10 for i in range(10)],500, camera=camera)]]
            pg.draw.polygon(screen, 'white', ps)
            ################

        self.self_light.light_draw(screen, camera)
        return super().light_draw(screen, camera)

    def draw(self, screen: pg.Surface, camera: pg.Rect):
        # self.img = IMGS['BACK'].copy()
        # self.img.blit(IMGS['PLAYER'].copy(), (0,0))
        # # if self.on_ground:
        # #     if self.xspeed == 0:
        # #         self.img.blit(PLAYER_LEGS_IDLE, (0, 53))
        # #     else:
        # #         self.img.blit(PLAYER_LEGS_R if self.r_leg else PLAYER_LEGS_L, (0, 53))
        # # else:
        # #     self.img.blit(PLAYER_LEGS_AIR, (0, 53))
        # # self.img.blit(PLAYER_LEGS_AIR, (0, 0))
        
        # off = 0 if self.look_r else -30
        # offy = 0 if not self.aiming else -5
        # if not self.on_ground and ((self.left and self.move_left and self.look_r) or (self.right and self.move_right and not self.look_r)) and self.wall_jump_kd<=0:
        #     self.img = pg.transform.rotate(self.img, -30)
        #     off = -15 if self.look_r else -55
        
        # # GUN IMG PROCC.
        # gun_img = pg.transform.rotate(weapons.GUNS[self.guns[self.gun]]['img'].copy(), self.angle-self.to_ang+(self.recoil*remap(self.shoot_kd, (0,weapons.GUNS[self.guns[self.gun]]['kd']))))
        # w,h=gun_img.get_width()/2,gun_img.get_height()/2
        # self.img.blit(gun_img, (gun_img.get_rect().x+30+weapons.GUNS[self.guns[self.gun]]['offx']-w, gun_img.get_rect().y+35+offy+weapons.GUNS[self.guns[self.gun]]['offy']-h))
        # if self.bonus['Double gun']>0: self.img.blit(gun_img, (gun_img.get_rect().x+35+weapons.GUNS[self.guns[self.gun]]['offx']-w, gun_img.get_rect().y+30+offy+weapons.GUNS[self.guns[self.gun]]['offy']-h))
        # # if not self.look_r and self.xspeed > 0: self.rotate()
        # # if self.look_r and self.xspeed < 0: self.rotate()

        # # WALL JUMP ROTATE
        # dw,dh=0,0
        # if self.wall_jump_kd>0:
        #     w,h = self.img.get_size()
        #     wall_ang = remap(self.wall_jump_kd, (0,500),(0,360))
        #     pivot = (12,10) if self.look_r else (-2,10)
        #     self.img = pg.transform.rotate(self.img, wall_ang)
        #     dw,dh =(self.img.get_width()/2, self.img.get_height()/2)- pg.math.Vector2(*pivot).rotate(-wall_ang)-((24,20) if self.look_r else (35,35))
        
        # if self.dead: self.img = PLAYER_IMG_DEAD
        # if not self.look_r: self.rotate()
        # if not self.dead:
        #     if self.dmg_timer > 0: self.img.blit(RED_TINT,(0,0),special_flags=pg.BLEND_RGB_ADD)
        #     # if self.inventory_kd>0:self.img.blit(self.font.render(f'[{self.guns[self.gun]}]',False,'white'), (-off,0))
        # # screen.fill('green',(self.pre_rect.x - camera.x, self.pre_rect.y + camera.y, self.pre_rect.w, self.pre_rect.h))
        
        # # if self.game.world.neo_mode:
        # #     neg = pg.Surface(self.img.get_size(), pg.SRCALPHA)
        # #     neg.fill((255, 255, 255))
        # #     neg.blit(self.img, (0, 0), special_flags=pg.BLEND_SUB)
        # #     self.img = neg

        # if self._hook and not (self.on_ground or self.right or self.left):
        #     w,h = self.img.get_size()
        #     ang = self.hook_ang-90
        #     pivot = (12,10) if self.look_r else (-2,10)
        #     self.img = pg.transform.rotate(self.img, ang)
        #     dw,dh =(self.img.get_width()/2, self.img.get_height()/2)- pg.math.Vector2(*pivot).rotate(-ang)-((24,20) if self.look_r else (35,35))

        # mask = pg.mask.from_surface(self.img).to_surface()
        # mask.set_colorkey('black')
        # if not self.dead and self.visible:
        #     if self._hook: pg.draw.line(screen, 'black', real(self.rect.center, camera), real(self.hook_point.xy, camera), 3)
        #     if self.bonus['Armor']>0:
        #         screen.blit(mask, (self.rect.x - camera.x+off-3-dw-2, self.rect.y - camera.y-dh))
        #         screen.blit(mask, (self.rect.x - camera.x+off-3-dw+2, self.rect.y - camera.y-dh))
        #         screen.blit(mask, (self.rect.x - camera.x+off-3-dw, self.rect.y - camera.y-dh-2))
        #         screen.blit(mask, (self.rect.x - camera.x+off-3-dw, self.rect.y - camera.y-dh+2))
        #     screen.blit(self.img, (self.rect.x - camera.x+off-3-dw, self.rect.y - camera.y-dh))
        # mask = pg.mask.from_surface(self.img).to_surface(setcolor=(0,0,0),unsetcolor=(0,0,0,0))
        # if not self.dead and self.visible:
        #     if self._hook: pg.draw.line(screen, 'black', real(self.rect.center, camera), real(self.hook_point.xy, camera), 3)
        #     screen.blit(mask, (self.rect.x - camera.x-2, self.rect.y - camera.y))
        #     screen.blit(mask, (self.rect.x - camera.x+2, self.rect.y - camera.y))
        #     screen.blit(mask, (self.rect.x - camera.x, self.rect.y - camera.y-2))
        #     screen.blit(mask, (self.rect.x - camera.x, self.rect.y - camera.y+2))
        self.rect.size = (40,40)
        
        # pg.draw.ellipse(screen, 'black', real(pg.Rect(self.rect.x+(self.speed.x/2)-2,self.rect.y+(self.speed.y/2)-2, self.rect.w-self.speed.x+4,self.rect.h-self.speed.y+4), camera))
        # pg.draw.ellipse(screen, 'lightgreen', real(pg.Rect(self.rect.x+(self.speed.x/2),self.rect.y+(self.speed.y/2), self.rect.w-self.speed.x,self.rect.h-self.speed.y), camera))
        if self._hook: pg.draw.line(screen, 'black', real(self.rect.center, camera), real(self.hook_point.xy, camera), 3)
        # SELECT IMAGE
        if self.on_ground and self.up:
            if self.left: self.img = IMGS2['UPDOWNLEFT'].copy()
            elif self.right: self.img = IMGS2['UPDOWNRIGHT'].copy()
            else: self.img = IMGS2['UPDOWN'].copy()
        elif self.on_ground:
            if self.right or self.left: 
                if self.right and self.left: self.img = IMGS2['DOWNBOTH'].copy()
                elif self.right: self.img = IMGS2['DOWNRIGHT'].copy()
                else: self.img = IMGS2['DOWNLEFT'].copy()
            else: self.img = IMGS2['DOWN'].copy()
        elif self.up:
            if self.right or self.left: 
                if self.right and self.left: self.img = IMGS2['UPBOTH'].copy()
                elif self.right: self.img = IMGS2['UPRIGHT'].copy()
                else: self.img = IMGS2['UPLEFT'].copy()
            else: self.img = IMGS2['UP'].copy()
        else:
            if self.right or self.left: self.img = (IMGS2['LEFT'].copy() if self.left else IMGS2['RIGHT'].copy())
            else: self.img = IMGS2['CENTER'].copy()

        shad = pg.mask.from_surface(self.img).to_surface(IMGS2['ALPHA'].copy(),setsurface=IMGS2['SHADOW'].copy(), unsetcolor=(0,0,0,0))
        self.img.blit(shad, (0,0))

        # DRAW FACE
        self.img.blit(IMGS2['FACE'],self.speed)

        # SQISH*
        offx, offy = 15 + abs(self.speed.x/2*1.5), 15 + abs(self.speed.y/2*1.5)
        if self.anim_flag: offy+=3
        self.img = pg.transform.scale(self.img, (self.img.get_width()-abs(self.speed.x*1.5),self.img.get_height()-abs(self.speed.y*1.5)+ (3 if self.anim_flag else 0)))

        # ROTATE
        w,h = self.img.get_size()
        ang = 0
        if self.wall_jump_kd>0: ang += remap(self.wall_jump_kd, (0,500),(0,360)) * (1 if self.look_r else -1)
        if self._hook and not (self.on_ground or self.right or self.left or self.up): ang += self.hook_ang-90
        self.img = pg.transform.rotate(self.img, ang)
        offx += self.img.get_width()/2 - w/2
        offy += self.img.get_height()/2 - h/2

        # DRAW GUN AND SECOND GUN
        gun_img = pg.transform.rotate(weapons.GUNS[self.guns[self.gun]]['img'].copy(), self.angle-self.to_ang+(self.recoil*remap(self.shoot_kd, (0,weapons.GUNS[self.guns[self.gun]]['kd']))))
        gnu_w,gun_h=gun_img.get_width()/2,gun_img.get_height()/2
        if not self.look_r: gun_img = pg.transform.flip(gun_img, True,False)
        self.img.blit(gun_img, (gun_img.get_rect().x+35+weapons.GUNS[self.guns[self.gun]]['offx']-gnu_w + self.img.get_width()/2 - w/2, gun_img.get_rect().y+40+weapons.GUNS[self.guns[self.gun]]['offy']-gun_h + self.img.get_height()/2 - h/2))
        if self.bonus['Double gun']>0: self.img.blit(gun_img, (gun_img.get_rect().x+40+weapons.GUNS[self.guns[self.gun]]['offx']-gnu_w + self.img.get_width()/2 - w/2, gun_img.get_rect().y+35+weapons.GUNS[self.guns[self.gun]]['offy']-gun_h + self.img.get_height()/2 - h/2))


        if self.dmg_timer > 0: self.img.blit(RED_TINT,(0,0),special_flags=pg.BLEND_RGB_ADD)
        mask = pg.mask.from_surface(self.img).to_surface(setcolor=((0,0,0) if not self.bonus['Armor']>0 else (255,255,255)),unsetcolor=(0,0,0,0))
        if not self.dead and self.visible:
            # OUTLINE
            screen.blit(mask, (self.rect.x - camera.x-2 - offx, self.rect.y - camera.y - offy))
            screen.blit(mask, (self.rect.x - camera.x+2 - offx, self.rect.y - camera.y - offy))
            screen.blit(mask, (self.rect.x - camera.x - offx, self.rect.y - camera.y-2 - offy))
            screen.blit(mask, (self.rect.x - camera.x - offx, self.rect.y - camera.y+2 - offy))

            screen.blit(self.img, (self.rect.x - camera.x - offx, self.rect.y - camera.y - offy))
        self.ui.render(self.game.screen)
