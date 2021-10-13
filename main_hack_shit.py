import pygame as pg

import os, traceback, socket, pickle, math
from random import randint as rd

import cfg
from game import player, level, core
from game.UI import Interface, Button, TextField
from game.utils import *


# Game by MaxGyverTech

with open('game/content/cursor.xbm') as c: 
    m = open('game/content/cursor_mask.xbm')
    cursor = pg.cursors.load_xbm(c,m)

# curs = 

class Game:
    def __init__(self):
        global sound
        self.res, self.fps, self.serv_ip = [cfg.screen_h, cfg.screen_v], cfg.fps, cfg.addr[0]
        print(f'Server: {self.serv_ip}')
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        pg.init()
        try:
            pg.mixer.init()
            self.sounds = True
        except pg.error:
            self.sounds = False
            print('No sounddevice, sounds ll turn off')

        self.screen = pg.display.set_mode(size=self.res, flags=pg.SCALED | pg.FULLSCREEN)
        self.frame = pg.Surface(self.res)
        self.clock = pg.time.Clock()
        self.pr = threading.Thread(target=self.await_data, daemon=True)
        self.camera = pg.Rect(0, -40, self.res[0], self.res[1])
        self.ui = Interface(self.sounds)
        self.world = level.World()
        self.player: player.Player = None
        self.players = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_port = 5001
        self.n = 0

        self.playing = False  # TODO: меню
        self.online = False
        self.pause = False
        self.searching = False
        self.shake = 0
        self.delta = 0.0

        pg.display.set_caption(cfg.GAMENAME)
        # pg.display.toggle_fullscreen()
        self.main_menu()
        pg.time.set_timer(pg.USEREVENT, 100)
        self.sock.settimeout(2.0)
        self.cat = pg.image.load('game/content/cat.png').convert_alpha()
        self.tint = pg.image.load('game/content/tint2.png').convert_alpha()

    def main_menu(self):
        pg.mouse.set_cursor(*pg.cursors.arrow)
        self.playing = False
        self.online = False
        self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        self.ui.set_ui([
            Button((100, 100), 'white', 'MENU', 80, ),
            Button((150, 200), 'white', 'New game', 50, self.start_game, 'darkgrey'),
            Button((150, 260), 'white', 'Level editor', 50, self.editor, 'darkgrey'),
            Button((150, 320), 'white', 'Join game', 50, self.join_game, 'darkgrey'),
            Button((150, 380), 'white', 'Exit', 50, exit, 'darkgrey'),
        ])
        

    def pause_menu(self):
        self.ui.clear()
        if not self.pause:
            self.pause = True
            self.ui.set_ui([
                Button((800, 400), 'white', 'Continue', 50, self.pause_menu, 'darkgrey'),
                Button((800, 460), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'),
                Button((800, 520), 'white', 'Exit', 50, exit, 'darkgrey'),
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
        self.world.open_world('levels/level.txt')
        self.playing = True
        self.player = player.Player(50, 0, 0, self)
        self.camera.x = 0
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
        pg.time.delay(500)
        for i in range(256):
            self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
            self.ui.clear()
            self.ui.set_ui([
                Button((350, 200), (i, 0, 0), 'GAME OVER', 80, ),
            ])
            self.draw()
            pg.display.update()
            pg.time.delay(10)
        self.ui.set_ui([
            Button((500, 300), 'white', 'Try again', 50, self.start_game, 'darkgrey'),
            Button((500, 360), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'),
            Button((500, 420), 'white', 'Exit', 50, exit, 'darkgrey'),
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
        # ofsetx, ofsety = 900,450
        # if self.player.rect.x < self.camera.x + ofsetx and self.camera.x > 0:
        #     self.camera.x -= (self.camera.x + ofsetx - self.player.rect.x) /20
        # if self.player.rect.right > self.camera.right - ofsetx and self.camera.right < self.world.rect.right:
        #     self.camera.x += (self.player.rect.right - self.camera.right + ofsetx)/20
        
        # if self.player.rect.y < self.camera.y + ofsety and self.camera.y > 0:
        #     self.camera.y -= (self.camera.y + ofsety - self.player.rect.y) /20
        # if self.player.rect.bottom > self.camera.bottom - ofsety and self.camera.bottom < self.world.rect.bottom:
        #     self.camera.y += (self.player.rect.bottom - self.camera.bottom + ofsety)/20
        ofsetx, ofsety = 930,450
        if self.player.rect.x < self.camera.x + ofsetx and self.camera.x > 0:
            self.camera.x -= (self.camera.x + ofsetx - self.player.rect.x) /20
        if self.player.rect.right > self.camera.right - ofsetx and self.camera.right < self.world.rect.right:
            self.camera.x += (self.player.rect.right - self.camera.right + ofsetx)/20
        
        if self.player.rect.y < self.camera.y + ofsety:
            self.camera.y -= (self.camera.y + ofsety - self.player.rect.y) /20
        if self.player.rect.bottom > self.camera.bottom - ofsety:
            self.camera.y += (self.player.rect.bottom - self.camera.bottom + ofsety)/20

    def update_control(self, event: pg.event.Event, camera: pg.Rect):
        d = {}
        # if event.type == pg.KEYDOWN:
        #     if event.key == pg.K_d: d['right'] = True
        #     if event.key == pg.K_a: d['left'] = True
        #     if event.key == pg.K_SPACE: d['up'] = True
        # if event.type == pg.KEYUP:
        #     if event.key == pg.K_d: d['right'] = False
        #     if event.key == pg.K_a: d['left'] = False
        #     if event.key == pg.K_SPACE: d['up'] = False
        # if event.type == pg.MOUSEMOTION:
        #     if self.player.rect.centerx <= event.pos[0] + camera.x:
        #         d['look_r'] = True
        #     else:
        #         d['look_r'] = False
        #     x, y = event.pos[0] + camera.x - self.player.rect.centerx, self.player.rect.centery - (event.pos[1] - 25)
        #     if x == 0: x = 1
        #     ang = int(math.degrees(math.atan(y / abs(x))))
        #     d['angle'] = ang
        # if event.type == pg.USEREVENT:
        #     self.player.r_leg = not self.player.r_leg
        # if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
        #     for i in range(1):
        #         s = core.Actor(event.pos[0],event.pos[1],40,40, bounce=0.4, friction=0.9)
        #         s.yspeed = -rd(6, 10)
        #         s.xspeed = (rd(0, 100) -50) / 10
        #         self.world.actors.append(s)
        #     d['shoot'] = True
        #     self.shake = 5

        # Python 3.10
        match event.type:
            case pg.KEYDOWN:
                match event.key:
                    case pg.K_d: d['right'] = True
                    case pg.K_a: d['left'] = True
                    case pg.K_SPACE: d['up'] = True
            case pg.KEYUP:
                match event.key:
                    case pg.K_d: d['right'] = False
                    case pg.K_a: d['left'] = False
                    case pg.K_SPACE: d['up'] = False
            case pg.MOUSEMOTION:
                if self.player.rect.centerx <= event.pos[0] + camera.x:
                    d['look_r'] = True
                else:
                    d['look_r'] = False
                x, y = event.pos[0] + camera.x - self.player.rect.centerx, self.player.rect.centery - (event.pos[1] - 25) - camera.y
                if x == 0: x = 1
                ang = int(math.degrees(math.atan(y / abs(x))))
                d['angle'] = ang
            case pg.USEREVENT:
                self.player.r_leg = not self.player.r_leg
            case pg.MOUSEBUTTONDOWN if event.button == pg.BUTTON_LEFT:
                for i in range(1):
                    s = core.Actor(event.pos[0],event.pos[1],40,40, bounce=0.4, friction=0.9)
                    s.yspeed = -rd(6, 10)
                    s.xspeed = (rd(0, 100) -50) / 10
                    self.world.actors.append(s)
                d['shoot'] = True
                self.shake = 5
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
            debug(f'FPS: {int(self.clock.get_fps())}',self.frame)
            debug(f'Actors: {len(self.world.actors)}', self.frame, y=30)
            debug(f'up:{self.player.on_ground} r:{self.player.right} l:{self.player.left}', self.frame, y=60)
            debug(self.camera, self.frame, y=90)
        else:
            self.frame.fill('black')
        self.ui.draw(self.frame)

    def event_loop(self):
        for event in pg.event.get():
            self.ui.update_buttons(event)

            # print(event, type(event))
            # if event.type == pg.QUIT: exit()
            
            # if self.playing and event.type in [pg.KEYUP, pg.KEYDOWN, pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.USEREVENT]:
            #     self.player.process_move(self.update_control(event, self.camera))

            # if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.pause_menu()

            match event.type:
                case pg.QUIT: exit()
                case pg.KEYDOWN if event.key == pg.K_ESCAPE: self.pause_menu()
                case pg.KEYUP | pg.KEYDOWN | pg.MOUSEMOTION | pg.MOUSEBUTTONDOWN | pg.USEREVENT if self.playing:
                    self.player.process_move(self.update_control(event, self.camera))
                
            

    def loop(self):
        self.event_loop()
        if self.playing:
            self.player.update_control(self.delta,self.world.get_blocks(self.player.pre_rect), self.world)
            self.world.update_actors(self.delta)

            if self.online:
                self.sock.sendall(pickle.dumps({'pos': self.player.rect.topleft, 'gun': self.player.gun,
                                                'n': self.player.n, 'xspeed': self.player.xspeed,
                                                'on_ground': self.player.on_ground, 'r_leg': self.player.r_leg,
                                                'look_r': self.player.look_r}))
            # if self.player.rect.x > 1000 and self.n != 1:
            #     self.set_level(1)
            # elif self.player.rect.x < 500 and self.n != 0:
            #     self.set_level(0)
            self.camera_update()

        self.screen.blit(self.frame, self.procces_camera_shake())
        self.draw()
        pg.display.update()

    def run(self):
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
