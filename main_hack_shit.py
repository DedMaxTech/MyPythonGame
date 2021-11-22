from time import sleep
import pygame as pg
import cProfile, pstats
import os, traceback, socket, pickle, math, glob
from random import randint as rd
from typing import List

import cfg

os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
pg.init()

try:
    pg.mixer.init()
    sounds = True
except pg.error:
    sounds = False
    print('No sounddevice, sounds ll turn off')

from game import *


# Game by MaxGyverTech

with open('game/content/cursor.xbm') as c: 
    m = open('game/content/cursor_mask.xbm')
    cursor = pg.cursors.load_xbm(c,m)

AUTOSAVE_EVENT = pg.USEREVENT+1

# curs = 
sf = pg.Surface((854*3,480*3))
sf.fill('black')
pg.draw.circle(sf,'white',(427,240), 50)
sf.set_colorkey('white')

font = pg.font.Font(cfg.font,60)
writing = False
class Game:
    def __init__(self):
        global sound
        self.res, self.fps, self.serv_ip = [cfg.screen_h, cfg.screen_v], cfg.fps, cfg.addr[0]
        print(f'Server: {self.serv_ip}')

        self.screen = pg.display.set_mode(size=self.res, flags=pg.SCALED | pg.FULLSCREEN)
        self.frame = pg.Surface(self.res)
        
        self.clock = pg.time.Clock()
        self.world_tick = 1.0
        self.pr = threading.Thread(target=self.await_data, daemon=True)
        self.camera = pg.Rect(0, -40, self.res[0], self.res[1])
        self.ui = Interface(sounds)
        self.world = level.World()
        self.player: player.Player = None
        self.players:List[player.Player] = []
        self.ais: List[enemies.MeleeAI] = []
        self.shits: List[core.Actor] = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 5001
        self.n = 0

        self.playing = False  # TODO: меню
        self.online,self.host = False,False
        self.pause = False
        self.searching = False
        self.shake = 0
        self.delta = 0.0
        self.millis = get_stat('time')
        self.w = 1
        self.level = 'levels/tutorial.txt'
        self.fps_alert = False

        pg.display.set_caption(cfg.GAMENAME)
        # pg.display.toggle_fullscreen()
        self.main_menu()
        pg.time.set_timer(pg.USEREVENT, 100)
        pg.time.set_timer(AUTOSAVE_EVENT, 10000)
        self.sock.settimeout(2.0)
        self.cat = pg.image.load('game/content/cat.png').convert_alpha()
        self.tint = pg.image.load('game/content/tint.png').convert_alpha()
        self.tint_slow = pg.image.load('game/content/tint_slow.png').convert_alpha()
        self.tint2 = pg.image.load('game/content/tint2.png').convert_alpha()

    def main_menu(self, add=[]):
        # pg.mouse.set_cursor(*pg.cursors.arrow)
        self.playing = False
        # if self.online: self.sock.close()
        self.online = False
        self.pause = False
        self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        tf = TextField((220,195+36), 'black', 'Code:',30,bg='white')
        self.ui.set_ui([Button((50, 50), 'white', 'MENU', 60, ),]+
            vertical(5,[
            Button((75, 120), 'white', 'New game', 30, self.select_level_menu, 'darkgrey'),
            Button((75, 155), 'white', 'Tutorial', 30, self.start_game, 'darkgrey'),
            Button((75, 190), 'white', 'Level editor', 30, self.editor, 'darkgrey'),
            Button((75, 200), 'white', 'Join game', 30, self.join_game, 'darkgrey',textfield=tf),
            Button((75, 260), 'white', 'Statistics', 30, self.stats_menu, 'darkgrey'),
            Button((75, 295), 'white', 'Exit', 30, exit, 'darkgrey'),
        ])+add+[tf])
    
    def select_level_menu(self):
        levels = dict()
        for i in glob.glob('levels/*.py'):
            i = i[i.index('\\')+1:-3]; levels[i.title()]=i
        self.ui.set_ui([Button((50, 50), 'white', 'Select level:', 40, ),Button((75, 400), 'white', 'Back', 25, self.main_menu, 'darkgrey'),]+vertical(5,
            [Button((75,100),'white',name,20,self.start_game,'red', args=levels[name]) for name in levels]
        ))
    
    def stats_menu(self, add=[]):
        y = 120
        bs = [Button((50, 50), 'white', 'YOUR STATS', 40, ),Button((75, 400), 'white', 'Back', 25, self.main_menu, 'darkgrey'),]
        d:dict = get_stat()
        for key in d:
            bs.append(Button((75, y), 'white',f'{key.title()}: {int(d[key])}', 20))
            y+=23
        self.ui.set_ui(bs+add)
        
    def pause_menu(self):
        if not self.pause:
            self.pause = True
            self.ui.set_ui([
                Button((400, 200), 'white', 'Continue', 25, self.pause_menu, 'darkgrey'),
                Button((400, 230), 'white', 'Respawn', 25, self.start_game, 'darkgrey', args=(self.level)),
                Button((400, 290), 'white', 'Main menu', 25, self.main_menu, 'darkgrey'),
                Button((400, 320), 'white', 'Exit', 25, exit, 'darkgrey'),
            ] + [Button((400, 260), 'white', 'Online', 25, self.create_game, 'darkgrey', ),] if not self.online else horizontal(5, [Button((400, 260), 'white', 'Offline', 25, self.close_game, 'darkgrey', ), Button((400, 260), 'white', f'Code to cennect: {self.ip.split(".")[-1]}', 25),]), anim=False)
            
            pg.mouse.set_cursor(*pg.cursors.arrow)
        else:
            # self.ui.set_ui(self.gameui)
            self.ui.clear()
            self.pause = False
            pg.mouse.set_cursor(*pg.cursors.diamond)

    def await_data(self):
        self.sock.settimeout(10)
        while True:
            try:
                data = pickle.loads(self.sock.recv(1024))
                ps = data.get('ps')
                for p in ps:
                    if not p: continue
                    global cur_p
                    n = p['n']
                    if n == self.player.n:
                        cur_p = self.player
                        continue
                    elif n not in [p.n for p in self.players]:
                        p = player.Player(0, 0, n)
                        self.players.append(p)
                        cur_p = p
                    else:
                        cur_p = [p for p in self.players if p.n == n][0]
                    cur_p.rect.topleft = p['pos']
                    cur_p.gun = p['gun']
                    cur_p.xspeed = p['xspeed']
                    cur_p.on_ground = p['on_ground']
                    cur_p.look_r = p['look_r']
                    cur_p.r_leg = p['r_leg']
            except ConnectionResetError:
                print('conn err')
                self.online = self.playing= False
                self.main_menu([Button((75, 290), 'white', 'Connection error', 30,bg='darkgrey'),])
            except Exception as e:
                print(traceback.format_exc())
    @threaded()
    def awaiting_conn(self):
        try:
            self.sock.listen()
            while self.host:
                conn, addr = self.sock.accept()
                print('new player ', addr)

        except Exception as e:
            print(e)

    @threaded()
    def awaiting_player_data(self,conn,addr):
        pass

    def join_menu(self, text, add=[]):
        self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        self.ui.set_ui([Button((700, 500), 'white', text, 50, ), ] + add)

    def editor(self):
        pg.display.set_caption('для продолженя игры закройте редактор')
        pg.display.toggle_fullscreen()
        os.system('python editor.py')
        pg.display.toggle_fullscreen()
        pg.display.set_caption(cfg.GAMENAME)
    @threaded()
    def start_zoom(self):
        self.zoom(3)
        sleep(0.75)
        self.zoom(1)

    def start_game(self, level='tutorial'):
        self.level = level
        self.ui.clear()
        x, y =self.world.open_world(level, game_inst=self)
        self.w = 2
        self.playing = True
        if self.pause: self.pause = False
        self.player = player.Player(x, y, 0, self)
        self.camera.center = (x,y)
        self.world.actors += [self.player]
        pg.mouse.set_cursor(*pg.cursors.diamond)

        self.start_zoom()

    # def join_game(self):
    #     try:
    #         self.sock.connect((self.serv_ip, self.port))
    #         data = pickle.loads(self.sock.recv(1024 * 4))
    #         self.world.open_world(data.get('level'))
    #         self.ui.clear()
    #         self.camera.x = 0
    #         self.player = player.Player(50, 0, data.get('n'), self)  # TODO: ONLINEEEEEE
    #         self.playing = True
    #         self.online = True
    #         self.pr.start()
    #     except socket.timeout:
    #         self.join_menu('Servers dont answer...',
    #                        [Button((800, 570), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'), ])
    #     except Exception as e:
    #         print(e)
    #         self.join_menu('Cant connect to servers:(',
    #                        [Button((800, 570), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'), ])

    #     self.loop()
    def join_game(self, port):
        try:
            ip = socket.gethostbyname(socket.getservbyname()).split('.')
            self.sock.connect(('.'.join(ip[:-1])+'.'+port, cfg.addr[1]))
            data = pickle.loads(self.sock.recv(1024 * 4))
            self.world.open_world(data.get('level'))
            self.ui.clear()
            self.camera.x = 0
            self.player = player.Player(50, 0, data.get('n'), self)  # TODO: ONLINEEEEEE
            self.playing = True
            self.online = True
            self.pr.start()
        except socket.timeout:
            self.join_menu('Servers dont answer...',
                           [Button((800, 570), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'), ])
        except Exception as e:
            print(e)
            self.join_menu('Cant connect to servers:(',
                           [Button((800, 570), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'), ])

        self.loop()
    
    def create_game(self):
        self.ip = socket.gethostbyname(socket.getservbyname())
        self.port = cfg.addr[1]
        self.sock.bind((self.ip, self.port))
        self.host = True
    
    def close_game(self):
        self.host=False
        self.sock.close()

    def death(self):
        self.zoom(1.5)

    @threaded(daemon=True)
    def set_level(self, floor=0, tpx=500):
        pos = (floor - self.n) * self.res[1]
        self.n = floor
        init_pos = self.camera.y
        for i in range(1000):
            p = init_pos + pos * (i / 1000)
            self.camera.y = p
            if i == tpx:
                self.player.rect.topleft = (800, (floor + 1) * 900)
            pg.time.wait(1)
        self.camera.y = init_pos + pos

    def camera_update(self):
        ofsetx, ofsety = 930,450
        d = self.frame.get_height()/10
        r = self.player.rect
        
        if self.player.aiming:
            x,y = vec_to_speed(300, -self.player.angle)
            x = x if self.player.look_r else -x
            r = pg.Rect(r.x+x,r.y+y,1,1)
            # self.world_tick = 0.3
        #     self.zoom(1.5)
        # else: self.zoom(1)   
        if r.x < self.camera.x + ofsetx:
            self.camera.x -= (self.camera.x + ofsetx - r.x) /d
        if r.right > self.camera.right - ofsetx:
            self.camera.x += (r.right - self.camera.right + ofsetx)/d

        if r.y < self.camera.y + ofsety:
            self.camera.y -= (self.camera.y + ofsety - r.y) /d
        if r.bottom > self.camera.bottom - ofsety:
            self.camera.y += (r.bottom - self.camera.bottom + ofsety)/d
    
    def process_zoom(self):
        size = self.frame.get_size()
        x,y=round((self.camera.w-size[0])/20), round((self.camera.h-size[1]) / 20)
        # self.frame = pg.Surface((size[0]+x,size[1]+y))
        self.frame =pg.transform.scale(self.frame, (size[0]+x,size[1]+y))

    def zoom(self,val):
        self.camera.size = (int(cfg.screen_h*val), int(cfg.screen_v*val))

    def update_control(self, event: pg.event.Event, camera: pg.Rect):
        d = {}
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d: d['right'] = True
            if event.key == pg.K_a: d['left'] = True
            if event.key == pg.K_SPACE: d['up'] = True
            if event.key == pg.K_q: d['tp'] = True
            if event.key == pg.K_r: d['reload'] = True
        if event.type == pg.KEYUP:
            if event.key == pg.K_d: d['right'] = False
            if event.key == pg.K_a: d['left'] = False
            if event.key == pg.K_SPACE: d['up'] = False
        if event.type == pg.MOUSEMOTION:
            if self.player.rect.centerx <= event.pos[0] + camera.x:
                d['look_r'] = True
            else:
                d['look_r'] = False
            # x, y = event.pos[0] + camera.x - self.player.rect.centerx, self.player.rect.centery - (event.pos[1] - 25)
            x, y = event.pos[0] + camera.x - self.player.rect.centerx,-((event.pos[1] + 10) + camera.y - self.player.rect.centery) 
            if x == 0: x = 1
            ang = int(math.degrees(math.atan(y / abs(x))))
            d['angle'] = ang
        if event.type == pg.USEREVENT:
            self.player.r_leg = not self.player.r_leg
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                d['shoot'] = True
                # self.shake = 5
            elif event.button == pg.BUTTON_WHEELUP:
                d['wheel'] = 1
            elif event.button == pg.BUTTON_WHEELDOWN:
                d['wheel'] = -1
            elif event.button == pg.BUTTON_RIGHT:
                d['aim'] = True
                # self.world_tick = 0.3
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == pg.BUTTON_LEFT:
                d['shoot'] = False
            elif event.button == pg.BUTTON_RIGHT:
                d['aim'] = False
                # self.world_tick = 1.0
        
        x,y = pg.mouse.get_pos()
        w,h = self.frame.get_size()
        x,y = remap(x, (0, cfg.screen_h), (0,w)), remap(y, (0, cfg.screen_v), (0,h))
        x, y =x+camera.x - self.player.rect.centerx, self.player.rect.centery - y - camera.y

        d['look_r'] = x>=0
        d['angle'] = angle((abs(x),-y))
        return d

    def procces_camera_shake(self):
        x, y = 0, 0
        if self.shake > 0:
            self.shake -= 1
            x = rd(-self.shake, self.shake)
            y = rd(-self.shake, self.shake)
        return x, y
    def draw(self):
        if self.playing:
            self.world.draw(self.frame, self.camera)
            # self.player.draw(self.frame, self.camera)

            for p in self.players:
                p.draw(self.frame, self.camera)
            
            # POST PROCESS
            if not cfg.potato:
                if self.world_tick == 1.0:
                    self.screen.blit(self.tint, (0, 0))
                else:
                    self.screen.blit(self.tint_slow, (0, 0))
            if self.w< sf.get_width():
                sf.fill('black')
                x,y = self.player.rect.centerx-self.camera.x, self.player.rect.centery-self.camera.y
                x,y = remap(x, (0,1280),(0,cfg.screen_h)),remap(y, (0,720),(0,cfg.screen_v))
                pg.draw.circle(sf,'white', (x,y), self.w)
                if self.player.dead:
                    text = font.render('Respawning...', False, (255,0,0))
                    text.set_alpha(remap(3000-self.player.die_kd, (1500,3000),(0,255)))
                    sf.blit(text, (300,100))
                self.screen.blit(sf,(0,0))
            debug(f'FPS: {int(self.clock.get_fps())} {"You have low FPS, game may work incorrect!" if self.fps_alert else ""}',self.frame)
            debug(f'Actors: {len(self.world.actors)}', self.frame, y=15)
            # debug(f'up:{self.player.on_ground} r:{self.player.right} l:{self.player.left}', self.frame, y=30)
            debug(f'pos: {self.player.rect.center} ang: {self.player.angle} xv: {self.player.xspeed:.1f} yv: {self.player.yspeed:.2f} hp: {self.player.hp} slow_mo: {self.player.aim_time}', self.frame,y = 30,)
            debug(f'{self.frame.get_size()} {self.camera.size}', self.frame,y = 45,)
        else:
            self.frame.fill('black')
        if self.pause: self.screen.blit(self.tint2, (0, 0))
        self.ui.draw(self.screen)

    def event_loop(self):
        global writing
        writing = pg.key.get_pressed()[pg.K_m]
        for event in pg.event.get():
            self.ui.update_buttons(event)
            if hasattr(event, 'pos'):
                x,y = self.frame.get_size()
                setattr(event, 'pos', (remap(event.pos[0], (0, cfg.screen_h), (0,x)), remap(event.pos[1], (0, cfg.screen_v), (0,y))))

            if event.type == pg.QUIT: exit()
            if self.playing and event.type in [pg.KEYUP, pg.KEYDOWN, pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN,pg.MOUSEBUTTONUP, pg.MOUSEWHEEL, pg.USEREVENT]:
                self.player.process_move(self.update_control(event, self.camera))

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.pause_menu()
            if event.type == AUTOSAVE_EVENT:
                write_stat('time', self.millis)

                
    def loop(self):
        self.event_loop()
        self.millis += self.delta/1000
        if self.playing and not self.pause:
            
            if self.player._delete: self.start_game(self.level)
            if self.player.dead and self.player.die_kd<=1500:
                if self.w > 1: self.w /= 1.1
            else:
                if self.w < sf.get_width(): self.w *= 1.1
            self.world_tick = 0.3 if self.player.aiming else 1.0
            self.player.update_control(self.delta*self.world_tick,self.world.get_blocks(self.player.pre_rect), self.world, self.world_tick)
            self.world.update_actors(self.delta*self.world_tick, self.player)

            if self.online:
                try:
                    self.sock.sendall(pickle.dumps({'pos': self.player.rect.topleft, 'gun': self.player.gun,
                                                    'n': self.player.n, 'xspeed': self.player.xspeed,
                                                    'on_ground': self.player.on_ground, 'r_leg': self.player.r_leg,
                                                    'look_r': self.player.look_r}))
                except ConnectionResetError:
                    print('conn err')
                    self.online = self.playing= False
                    self.main_menu([Button((75, 290), 'white', 'Connection error', 30,bg='darkgrey'),])
            self.camera_update()
            self.process_zoom()
            if self.clock.get_fps()<=35: self.fps_alert=True

        self.screen.blit(pg.transform.scale(self.frame, self.res), self.procces_camera_shake())
        self.draw()
        pg.display.update()

    @threaded()
    def resize(self):
        while True:
            x,y = input().split(' ')
            self.screen = pg.display.set_mode(size=(int(x), int(y)), flags=pg.SCALED | pg.FULLSCREEN)

    def run(self):
        print(repr(get_stat()))
        # self.resize()
        while True:
            if writing:
                with cProfile.Profile() as pr:
                    self.loop()
                stats = pstats.Stats(pr)
                stats.sort_stats(pstats.SortKey.TIME)
                stats.dump_stats('stat.prof')
            else: self.loop()
            self.delta = self.clock.tick(cfg.fps)
       

if __name__ == '__main__':
    print(socket.gethostbyname(socket.gethostname()))
    game = Game()
    try:
        game.run()
    except Exception as e:
        print(traceback.format_exc())
        pg.display.toggle_fullscreen()
