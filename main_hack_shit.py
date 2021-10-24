import pygame as pg

import os, traceback, socket, pickle, math
from random import randint as rd
from typing import List

import cfg

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
sf = pg.Surface((854,480))
sf.fill('black')
pg.draw.circle(sf,'white',(427,240), 50)
sf.set_colorkey('white')

class Game:
    def __init__(self):
        global sound
        self.res, self.fps, self.serv_ip = [cfg.screen_h, cfg.screen_v], cfg.fps, cfg.addr[0]
        print(f'Server: {self.serv_ip}')
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        pg.init()
        
        # print(not pg.mixer.get_init()is No40)

        self.screen = pg.display.set_mode(size=self.res, flags=pg.SCALED | pg.FULLSCREEN | pg.HWSURFACE)
        self.frame = pg.Surface(self.res)
        self.clock = pg.time.Clock()
        self.pr = threading.Thread(target=self.await_data, daemon=True)
        self.camera = pg.Rect(0, -40, self.res[0], self.res[1])
        self.ui = Interface(sounds)
        self.world = level.World()
        self.player: player.Player = None
        self.players:List[player.Player] = []
        self.ais: List[enemies.AI] = []
        self.shits: List[core.Actor] = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_port = 5001
        self.n = 0

        self.playing = False  # TODO: меню
        self.online = False
        self.pause = False
        self.searching = False
        self.shake = 0
        self.delta = 0.0
        self.millis = get_stat('time')
        self.w = 1

        pg.display.set_caption(cfg.GAMENAME)
        # pg.display.toggle_fullscreen()
        self.main_menu()
        pg.time.set_timer(pg.USEREVENT, 100)
        pg.time.set_timer(AUTOSAVE_EVENT, 10000)
        self.sock.settimeout(2.0)
        self.cat = pg.image.load('game/content/cat.png').convert_alpha()
        self.tint = pg.image.load('game/content/tint.png').convert_alpha()
        self.tint2 = pg.image.load('game/content/tint2.png').convert_alpha()

    def main_menu(self, add=[]):
        # pg.mouse.set_cursor(*pg.cursors.arrow)
        self.playing = False
        # if self.online: self.sock.close()
        self.online = False
        self.pause = False
        self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        self.ui.set_ui([
            Button((50, 50), 'white', 'MENU', 60, ),
            Button((75, 120), 'white', 'New game', 30, self.start_game, 'darkgrey'),
            Button((75, 155), 'white', 'Level editor', 30, self.editor, 'darkgrey'),
            Button((75, 190), 'white', 'Join game', 30, self.join_game, 'darkgrey'),
            Button((75, 225), 'white', 'Statistics', 30, self.stats_menu, 'darkgrey'),
            Button((75, 260), 'white', 'Exit', 30, exit, 'darkgrey'),
            # Button((600, 400), 'white', f'Secs in game: {self.millis:.1f}', 20, ),
        ]+add)
    
    def stats_menu(self, add=[]):
        y = 120
        bs = [Button((50, 50), 'white', 'YOUR STATS', 40, ),Button((75, 400), 'white', 'Back', 25, self.main_menu, 'darkgrey'),]
        d:dict = get_stat()
        for key in d:
            bs.append(Button((75, y), 'white',f'{key.title()}: {int(d[key])}', 20))
            y+=23
        self.ui.set_ui(bs+add)
        
    def pause_menu(self):
        self.ui.clear()
        if not self.pause:
            self.pause = True
            self.ui.set_ui([
                Button((400, 200), 'white', 'Continue', 25, self.pause_menu, 'darkgrey'),
                Button((400, 230), 'white', 'Respawn', 25, self.start_game, 'darkgrey'),
                Button((400, 260), 'white', 'Main menu', 25, self.main_menu, 'darkgrey'),
                Button((400, 290), 'white', 'Exit', 25, exit, 'darkgrey'),
            ])
            pg.mouse.set_cursor(*pg.cursors.arrow)
        else:
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

    def start_game(self):
        self.ui.clear()
        x, y =self.world.open_world('levels/level.txt')
        self.w = 2
        self.playing = True
        if self.pause: self.pause = False
        self.player = player.Player(x, y, 0, self)
        self.camera.x = 0
        # e = 
        self.world.actors += [self.player]
        pg.mouse.set_cursor(*pg.cursors.diamond)

    def join_game(self):
        try:
            self.sock.connect((self.serv_ip, self.serv_port))
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

    def death(self):
        self.playing = False
        self.frame.fill('black')
        pg.time.delay(500)
        for i in range(256):
            self.frame.fill('black')
            self.ui.clear()
            self.ui.set_ui([
                Button((150, 100), (i, 0, 0), 'GAME OVER', 40, ),
            ])
            # self.draw()
            self.ui.draw(self.frame)
            pg.display.update()
            pg.time.delay(10)
        self.ui.set_ui([
            Button((350, 200), 'white', 'Try again', 25, self.start_game, 'darkgrey'),
            Button((350, 230), 'white', 'Main menu', 25, self.main_menu, 'darkgrey'),
            Button((350, 260), 'white', 'Exit', 25, exit, 'darkgrey'),
        ])

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
        if self.player.rect.x < self.camera.x + ofsetx:
            self.camera.x -= (self.camera.x + ofsetx - self.player.rect.x) /40
        if self.player.rect.right > self.camera.right - ofsetx:
            self.camera.x += (self.player.rect.right - self.camera.right + ofsetx)/40
        
        if self.player.rect.y < self.camera.y + ofsety:
            self.camera.y -= (self.camera.y + ofsety - self.player.rect.y) /40
        if self.player.rect.bottom > self.camera.bottom - ofsety:
            self.camera.y += (self.player.rect.bottom - self.camera.bottom + ofsety)/40

    def update_control(self, event: pg.event.Event, camera: pg.Rect):
        d = {}
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d: d['right'] = True
            if event.key == pg.K_a: d['left'] = True
            if event.key == pg.K_SPACE: d['up'] = True
            if event.key == pg.K_q: d['tp'] = True
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
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            # for i in range(1):
            #     s = core.Actor(event.pos[0],event.pos[1],40,40, bounce=0.4, friction=0.9)
            #     s.yspeed = -rd(6, 10)
            #     s.xspeed = (rd(0, 100) -50) / 10
            #     self.world.actors.append(s)
            d['shoot'] = True
            self.shake = 5
        
        x,y = pg.mouse.get_pos()
        x, y =x+camera.x - self.player.rect.centerx, self.player.rect.centery - y - camera.y
        # print(x,y)
        d['look_r'] = x>=0
        d['angle'] = angle((abs(x),y))
        # Python 3.10
        # match event.type:
        #     case pg.KEYDOWN:
        #         match event.key:
        #             case pg.K_d: d['right'] = True
        #             case pg.K_a: d['left'] = True
        #             case pg.K_SPACE: d['up'] = True
        #     case pg.KEYUP:
        #         match event.key:
        #             case pg.K_d: d['right'] = False
        #             case pg.K_a: d['left'] = False
        #             case pg.K_SPACE: d['up'] = False
        #     case pg.MOUSEMOTION:
        #         if self.player.rect.centerx <= event.pos[0] + camera.x:
        #             d['look_r'] = True
        #         else:
        #             d['look_r'] = False
        #         x, y = event.pos[0] + camera.x - self.player.rect.centerx, self.player.rect.centery - (event.pos[1] - 25) - camera.y
        #         if x == 0: x = 1
        #         ang = int(math.degrees(math.atan(y / abs(x))))
        #         d['angle'] = ang
        #     case pg.USEREVENT:
        #         self.player.r_leg = not self.player.r_leg
        #     case pg.MOUSEBUTTONDOWN if event.button == pg.BUTTON_LEFT:
        #         # for i in range(1):
        #         #     s = core.Actor(event.pos[0],event.pos[1],40,40, bounce=0.4, friction=0.9)
        #         #     s.yspeed = -rd(6, 10)
        #         #     s.xspeed = (rd(0, 100) -50) / 10
        #         #     self.world.actors.append(s)
        #         d['shoot'] = True
        #         self.shake = 5
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
            self.player.draw(self.frame, self.camera)

            for p in self.players:
                p.draw(self.frame, self.camera)
            
            # POST PROCESS
            self.frame.blit(self.tint, (0, 0))
            if self.w< 854:
                sf.fill('black')
                pg.draw.circle(sf,'white', (self.player.rect.x-self.camera.x, self.player.rect.y-self.camera.y), self.w)
                self.frame.blit(sf,(0,0))
            debug(f'FPS: {int(self.clock.get_fps())}',self.frame)
            debug(f'Actors: {len(self.world.actors)}', self.frame, y=15)
            # debug(f'up:{self.player.on_ground} r:{self.player.right} l:{self.player.left}', self.frame, y=30)
            debug(f'pos: {self.player.rect.center} ang: {self.player.angle} xv: {self.player.xspeed:.1f} yv: {self.player.yspeed:.2f} hp: {self.player.hp}', self.frame,y = 30,)
            debug(self.camera, self.frame,y = 45,)
        else:
            self.frame.fill('black')
        if self.pause: self.frame.blit(self.tint2, (0, 0))
        self.ui.draw(self.frame)

    def event_loop(self):
        for event in pg.event.get():
            self.ui.update_buttons(event)

            # print(event, type(event))
            if event.type == pg.QUIT: exit()
            
            if self.playing and event.type in [pg.KEYUP, pg.KEYDOWN, pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.USEREVENT]:
                self.player.process_move(self.update_control(event, self.camera))

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.pause_menu()
            if event.type == AUTOSAVE_EVENT:
                write_stat('time', self.millis)

            # match event.type:
            #     case pg.QUIT: exit()
            #     case pg.KEYDOWN if event.key == pg.K_ESCAPE: self.pause_menu()
            #     case pg.KEYUP | pg.KEYDOWN | pg.MOUSEMOTION | pg.MOUSEBUTTONDOWN | pg.USEREVENT if self.playing:
            #         self.player.process_move(self.update_control(event, self.camera))
                
    def loop(self):
        self.event_loop()
        self.millis += self.delta/1000
        if self.playing and not self.pause:
            if self.player._delete: self.start_game()
            if self.w < 854: self.w *= 1.1
            self.player.update_control(self.delta,self.world.get_blocks(self.player.pre_rect), self.world)
            self.world.update_actors(self.delta, self.player)

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
            # if self.player.rect.x > 1000 and self.n != 1:
            #     self.set_level(1)
            # elif self.player.rect.x < 500 and self.n != 0:
            #     self.set_level(0)
            self.camera_update()

        self.screen.blit(self.frame, self.procces_camera_shake())
        self.draw()
        pg.display.update()

    def run(self):
        print(repr(get_stat()))
        while True:
            self.loop()
            self.delta = self.clock.tick(cfg.fps)


if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except Exception as e:
        print(traceback.format_exc())
        pg.display.toggle_fullscreen()
