import os, traceback, socket, pickle, math
from random import randint as rd
import cfg
from game import player, level, core
from game.UI import Interface, Button

from game.utils import *



class Game:
    def __init__(self):
        self.res, self.fps, self.serv_ip = [cfg.screen_h, cfg.screen_v], cfg.fps, cfg.addr[0]
        print(self.serv_ip)
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        pg.init()

        self.screen = pg.display.set_mode(size=self.res, flags=pg.SCALED, vsync=True)
        self.frame = pg.Surface(self.res)
        self.clock = pg.time.Clock()
        self.pr = threading.Thread(target=self.await_data, daemon=True)
        self.camera = pg.Rect(0, 40, self.res[0], self.res[1])
        self.ui = Interface()
        self.world = level.World()
        self.player: player.Player = None
        self.players = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_port = 5001
        self.n = 0

        self.playing = False  # TODO: меню
        self.online = False
        self.searching = False
        self.shake = 0

        pg.display.set_caption(cfg.GAMENAME)
        pg.display.toggle_fullscreen()
        self.main_menu()
        pg.time.set_timer(pg.USEREVENT, 100)
        self.sock.settimeout(2.0)
        self.cat = cat_img = pg.image.load('game/content/cat.png').convert_alpha()
        self.tint = pg.image.load('game/content/tint2.png').convert_alpha()

        self.shit = []

    def main_menu(self):
        self.playing = False;
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
        if self.playing:
            self.playing = False
            self.ui.set_ui([
                Button((500, 200), 'white', 'Continue', 50, self.pause_menu, 'darkgrey'),
                Button((500, 260), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'),
                Button((500, 320), 'white', 'Exit', 50, exit, 'darkgrey'),
            ])
        else:
            self.playing = True

    def await_data(self):
        self.sock.settimeout(10)
        while True:
            try:
                data = pickle.loads(self.sock.recv(1024))
                print(data)
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
        os.system('python game/editor.py')
        pg.display.toggle_fullscreen()
        pg.display.set_caption(cfg.GAMENAME)

    def start_game(self):
        self.ui.clear()
        self.world.open_world('levels/level.txt')
        self.playing = True
        self.player = player.Player(50, 0, 0, self)
        self.camera.x = 0

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
        pos = (floor - self.n) * -self.res[1]
        self.n = floor
        init_pos = self.camera.y
        for i in range(1000):
            p = init_pos + pos * (i / 1000)
            self.camera.y = p
            if i == tpx:
                print('move player')
                self.player.rect.topleft = (800, (floor + 1) * 900)
            pg.time.delay(1)
        self.camera.y = init_pos + pos

        # print(floor, init_pos, pos)

    def camera_update(self):
        if self.player.rect.x < self.camera.x + 400 and self.camera.x > 0:
            self.camera.x -= self.camera.x + 400 - self.player.rect.x
        if self.player.rect.right > self.camera.right - 400 and self.camera.right < self.world.rect.right:
            self.camera.x += self.player.rect.right - self.camera.right + 400

    def update_control(self, event: pg.event.Event, camera: pg.Rect):
        d = {}
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d: d['right'] = True
            if event.key == pg.K_a: d['left'] = True
            if event.key == pg.K_SPACE: d['up'] = True
        if event.type == pg.KEYUP:
            if event.key == pg.K_d: d['right'] = False
            if event.key == pg.K_a: d['left'] = False
            if event.key == pg.K_SPACE: d['up'] = False
        if event.type == pg.MOUSEMOTION:
            if self.player.rect.centerx <= event.pos[0] + camera.x:
                d['look_r'] = True
            else:
                d['look_r'] = False
            x, y = event.pos[0] + camera.x - self.player.rect.centerx, self.player.rect.centery - (event.pos[1] - 25)
            if x == 0: x = 1
            ang = int(math.degrees(math.atan(y / abs(x))))
            d['angle'] = ang
        if event.type == pg.USEREVENT:
            self.player.r_leg = not self.player.r_leg
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            for i in range(100):
                s = core.Actor(event.pos[0],event.pos[1],40,40, bounce=0.4)
                s.yvel = -rd(6,10)
                s.xvel = rd(-40,50) / 10
                self.shit.append(s)
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
            for i in self.shit:
                self.frame.blit(self.cat, (i.rect.x - self.camera.x, i.rect.y + self.camera.y, i.rect.w, i.rect.h))

            for p in self.players:
                p.draw(self.frame, self.camera)
            # debug(self.shit.xvel, self.screen)
            # POST PROCESS
            # self.frame.blit(self.tint, (0, 0))
            debug(self.clock.get_fps(),self.frame)
            debug(len(self.shit), self.frame, y=30)
        self.ui.draw(self.frame)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.ui.update_buttons(event)

            if self.playing and event.type in [pg.KEYUP, pg.KEYDOWN, pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.USEREVENT]:
                self.player.process_move(self.update_control(event, self.camera))

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.pause_menu()

    def loop(self):
        self.event_loop()
        if self.playing:
            self.player.update(self.world.get_blocks(), self.world)
            [i.update(self.world.blocks) for i in self.shit]
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
            self.clock.tick(self.fps)


if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except Exception as e:
        print(traceback.format_exc())
        pg.display.toggle_fullscreen()
