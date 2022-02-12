from time import sleep
import pygame as pg
import os, traceback, socket, pickle, math, glob, subprocess, zlib,cProfile, pstats
from random import randint as rd
from typing import List

import cfg

# Game by MaxGyverTech
# 

os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
pg.init()

try:
    pg.mixer.init()
    sounds = True
except pg.error:
    sounds = False
    print('No sounddevice, sounds ll turn off')

from game import *




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

load_screen = pg.Surface((cfg.screen_h,cfg.screen_v))
load_screen.blit(font.render('Loading...', False, 'white'),(320,190))

writing = False

bad_data = pg.Surface((854,480))
bad_data.fill('white')
bad_data = bad_data.get_view()

class Game:
    def __init__(self):
        self.res, self.fps, self.serv_ip = [cfg.screen_h, cfg.screen_v], cfg.fps, cfg.addr[0]
        print(f'Server: {self.serv_ip}')

        self.screen = pg.display.set_mode(size=self.res, flags=pg.SCALED | pg.FULLSCREEN)
        self.frame = pg.Surface(self.res)
        
        self.clock = pg.time.Clock()
        self.world_tick = 1.0
        self.pr = threading.Thread(target=self.await_data, daemon=True)
        self.camera = pg.Rect(0, -40, self.res[0], self.res[1])
        self.ui = Interface()
        self.world = level.World()
        self.player: player.Player = None
        self.players:List[player.Player] = []
        self.ais: List[enemies.MeleeAI] = []
        self.shits: List[core.Actor] = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 5001
        self.n = 0

        self.playing = False  # TODO: меню
        self.online,self.host = Status.Offline,False
        self.addr = ('',0)
        self.addrs = {}
        self.pause = False
        self.searching = False
        self.shake = 0
        self.delta = 0.0
        self._zoom = 1
        self._curzoom = 1

        self.stats = get_stat()
        self.w = 1
        self.v=1
        self.level = 'levels/tutorial.txt'
        self.fps_alert = False
        self.camera_target = None
        self.debug = False

        self.stream_fps = 0

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
        self.online = Status.Offline
        self.pause = False
        self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        tf = TextField((220,195+36), 'black', 'Code:',30,bg='white',clear_on_click=True)
        b = Button((0,0), 'white', 'delete', 30, bg='darkgrey')
        b.func=b.delete
        self.ui.set_ui([Button((50, 50), 'white', 'MENU', 60, ),]+
            vertical(5,[
            Button((75, 120), 'white', 'New game', 30, self.select_level_menu, 'darkgrey'),
            Button((75, 155), 'white', 'Tutorial', 30, self.start_game, 'darkgrey'),
            Button((75, 190), 'white', 'Level editor', 30, self.editor, 'darkgrey'),
            Button((75, 200), 'white', 'Join game', 30, self.join_game, 'darkgrey',textfield=tf),
            Button((75, 260), 'white', 'Statistics', 30, self.stats_menu, 'darkgrey'),
            Button((75, 295), 'white', 'Exit', 30, exit, 'darkgrey'),
        ])+add+[tf,])
    
    def select_level_menu(self):
        levels = dict()
        for i in glob.glob('levels/*.py'):
            i = i[i.index('\\')+1:-3]; levels[i.title()]=i
        self.ui.set_ui([Button((50, 50), 'white', 'Select level:', 40, ),Button((75, 400), 'white', 'Back', 25, self.main_menu, 'darkgrey'),]+vertical(5,
            [Button((75,100),'white',name,20,self.start_game,'red', args=levels[name]) for name in levels]
        ))
    
    def stats_menu(self, add=[]):
        bs = [Button((50, 50), 'white', 'YOUR STATS', 40, ),]
        d:dict = self.stats
        k = f'{remap(d["time in air"],(0,d["time on ground"])):.2f}/1.0' if d["time in air"]<d["time on ground"] else f'1.0/{remap(d["time on ground"],(0,d["time in air"])):.2f}'
        bs+=[VBox(3,(75,120),widgets=[
                Button((0,0), 'white',f'Time in game:', 20),
                Button((0,0), 'white',f'Damage you done:', 20),
                Button((0,0), 'white',f'Damage you received:', 20),
                Button((0,0), 'white',f'You shoot:', 20),
                Button((0,0), 'white',f'You was in air:', 20),
                Button((0,0), 'white',f'Time in air/on ground:', 20),
                Button((75, 400), 'white', 'Back', 25, self.main_menu, 'darkgrey'),
            ]),
            VBox(3,(75,120),(600,1000), anchor_h=UI.RIGHT, widgets=[
                Button((0,0), 'white',f'{int(d["time"]/60)} mins.', 20),
                Button((0,0), 'white',f'{int(d["done damage"])} hp', 20),
                Button((0,0), 'white',f'{int(d["received damage"])} hp', 20),
                Button((0,0), 'white',f'{d["shoots"]} bullets', 20),
                Button((0,0), 'white',f'{int(d["time in air"]/60)} mins.', 20),
                Button((0,0), 'white',k, 20),
            ])]
        # for key in d:
        #     bs.append(Button((75, y), 'white',f'{key.title()}: {int(d[key])}', 20))
        #     y+=23
        self.ui.set_ui(bs+add)
        
    def pause_menu(self):
        if not self.pause:
            self.pause = True
            self.ui.set_ui([
                Button((400, 200), 'white', 'Continue', 25, self.pause_menu, 'darkgrey'),
                Button((400, 230), 'white', 'Respawn', 25, self.start_game, 'darkgrey', args=(self.level)),
                Button((400, 290), 'white', 'Main menu', 25, self.main_menu, 'darkgrey'),
                Button((400, 320), 'white', 'Exit', 25, exit, 'darkgrey'),
            ] + ([Button((400, 260), 'white', 'Online', 25, self.create_game, 'darkgrey', ),] if self.online == Status.Offline else horizontal(5, [Button((400, 260), 'white', 'Offline', 25, self.close_game, 'darkgrey', ), Button((400, 260), 'white', f'Code to cennect: {self.addr[0].split(".")[-1]}', 25),])), anim=False)
            
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
                self.online = Status.Offline
                self.playing= False
                self.main_menu([Button((75, 290), 'white', 'Connection error', 30,bg='darkgrey'),])
            except Exception as e:
                print(traceback.format_exc())
    @threaded()
    def awaiting_conn(self):
        while 1:
            try:
                if self.online is Status.Host:
                    d,addr = self.sock.recvfrom(4096)
                    # print(d,addr,d == b'hello',addr not in self.addrs.keys())
                    if addr not in self.addrs.keys():
                        if d == b'hello':
                            print('sana pidor')
                            p = player.Player(*self.world.spawn_pos, game_inst=self)
                            self.addrs[addr] = [5000,p]
                            self.world.actors.append(p)
                    else:
                        p = self.addrs[addr][1]
                        data = pickle.loads(d)
                        if data: print(data)
                        p.process_move(data)
                        self.addrs[addr] = [5000,p]
                else:
                    time.sleep(1)
            except socket.timeout:
                pass

    # @threaded()
    # def awaiting_player_data(self):
    #     while 1:
    #         try:
    #             if self.online is Status.Host:
    #                 d,addr = self.sock.recvfrom(4096)
                    
    #             else:
    #                 time.sleep(1)
    #         except socket.timeout:
    #             pass

    def join_menu(self, text, add=[]):
        self.frame.fill('black', [0, 0, self.res[0], self.res[1] + 40])
        self.ui.clear()
        self.ui.set_ui([Button((700, 500), 'white', text, 50, ), ] + add)

    def editor(self):
        pg.display.set_caption('для продолженя игры закройте редактор')
        pg.display.toggle_fullscreen()
        # os.system('python editor.py')
        subprocess.run('python editor.py')
        pg.display.toggle_fullscreen()
        pg.display.set_caption(cfg.GAMENAME)
    @threaded()
    def start_zoom(self, level):
        self.zoom(3)
        # if f'levels.{level}' not in sys.modules:sleep(1)
        sleep(0.85)
        self.zoom(1)

    def start_game(self, level='tutorial'):
        self.screen.blit(load_screen,(0,0))
        pg.display.flip()
        self.playing = True
        self.level = level
        self.ui.clear()
        pos, guns =self.world.open_world(level, game_inst=self)
        self.w=1
        self.v=cfg.screen_h
        self.camera_target=None
        if self.pause: self.pause = False
        self.player = player.Player(*pos, 0, self)
        for i in self.addrs.values():
            p = player.Player(*pos, 0, self)
            i[1] = p
            self.world.actors.append(p)
        s = objects.SpawningPortal(*pos, self)
        self.player.guns = list(set(self.player.guns+guns))
        self.camera.center = pos
        self.world.actors += [self.player,s]
        pg.mouse.set_cursor(*pg.cursors.diamond)

        self.start_zoom(level)

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
    
    @threaded()
    def screen_stream(self,fps=60):
        ip = (socket.gethostbyname(socket.gethostname()),5001)
        self.addr = ip
        print('Self ip:',ip)
        self.sock.bind(ip)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144*2)
        print(self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
        
        buf_size = 1024
        self.awaiting_conn()
        # self.awaiting_player_data()
        kd = pg.time.Clock()
        while 'always':
            if self.online is not Status.Host: kd.tick(fps)
            if writing:
                with cProfile.Profile() as pr:
                    self.send_screen(kd, fps,buf_size)
                stats = pstats.Stats(pr)
                stats.sort_stats(pstats.SortKey.TIME)
                stats.dump_stats('stat2.prof')
            else: self.send_screen(kd, fps,buf_size)

    
    def send_screen(self,kd,fps=60, buf_size=1024,compress_level=2):
        predata = zlib.compress(pg.image.tostring(self.screen,'RGB'),compress_level)
        k = len(predata)//buf_size
        data = []
        for i in range(k):
            data.append(predata[:buf_size])
            predata = predata[buf_size:]
        data.append(predata)
        for addr in self.addrs:
            for d in data:
                self.sock.sendto(d,addr)
            self.sock.sendto(b'stop',addr)
        kd.tick(fps)
        self.stream_fps = kd.get_fps()        
    
    
    def join_game(self, port):
        # try:
        ip = socket.gethostbyname(socket.gethostname()).split('.')
        addr = ('.'.join(ip[:-1])+'.'+port, cfg.addr[1])
        self.sock.settimeout(2)
        self.sock.sendto(b'hello',addr)
        self.online = Status.Listen
        self.addr = addr
        self.get_frames()
        #     self.world.open_world(data.get('level'))
        #     self.ui.clear()
        #     self.camera.x = 0
        #     self.player = player.Player(50, 0, data.get('n'), self)  # TODO: ONLINEEEEEE
        #     self.playing = True
        #     self.online = True
        #     self.pr.start()
        # except socket.timeout:
        #     self.join_menu('Servers dont answer...',
        #                    [Button((800, 570), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'), ])
        # except Exception as e:
        #     print(e)
        #     self.join_menu('Cant connect to servers:(',
        #                    [Button((800, 570), 'white', 'Main menu', 50, self.main_menu, 'darkgrey'), ])

        # self.loop()
    
    def create_game(self):
        self.online = Status.Host
        self.pause_menu()
        self.pause_menu()

    
    def close_game(self):
        self.online = Status.Offline
        # self.sock.close()
        self.pause_menu()
        self.pause_menu()

    def death(self):
        self.zoom(1.5)

    def camera_update(self):
        k = self.delta/core.def_tick
        d = self.frame.get_height()/15/k/self._curzoom
        r = self.player.rect
        
        if self.camera_target:
            r = self.camera_target
        else:
            if self.player.aiming:
                x,y = vec_to_speed(300, -self.player.angle)
                x = x if self.player.look_r else -x
                r = pg.Rect(r.x+x,r.y+y,1,1)

        self.camera.centerx-= (self.camera.centerx-r.centerx)/d
        self.camera.centery-= (self.camera.centery-r.centery)/d

    
    def process_zoom(self):
        size = self.frame.get_size()
        self._curzoom=size[0]*self._zoom/self.camera.w
        self.frame =pg.transform.scale(self.frame, (size[0]+int(((self.camera.w-size[0])/30)),size[1]+int((self.camera.h-size[1]) / 30)))

    def zoom(self,val):
        self.camera.size = (int(cfg.screen_h*val), int(cfg.screen_v*val))
        self._zoom = val

    def update_control(self, event: pg.event.Event, camera: pg.Rect):
        d = {}
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d: d['right'] = True
            if event.key == pg.K_a: d['left'] = True
            if event.key == pg.K_SPACE: d['up'] = True
            if event.key == pg.K_q: d['tp'] = True
            if event.key == pg.K_r: d['reload'] = True
            if event.key == pg.K_g: d['grenade']=True
            if event.key == pg.K_n: self.debug = not self.debug
        if event.type == pg.KEYUP:
            if event.key == pg.K_d: d['right'] = False
            if event.key == pg.K_a: d['left'] = False
            if event.key == pg.K_SPACE: d['up'] = False
        # if event.type == pg.MOUSEMOTION:
        #     if self.player.rect.centerx <= event.pos[0] + camera.x:
        #         d['look_r'] = True
        #     else:
        #         d['look_r'] = False
        #     # x, y = event.pos[0] + camera.x - self.player.rect.centerx, self.player.rect.centery - (event.pos[1] - 25)
        #     x, y = event.pos[0] + camera.x - self.player.rect.centerx,-((event.pos[1] + 10) + camera.y - self.player.rect.centery) 
        #     if x == 0: x = 1
        #     ang = int(math.degrees(math.atan(y / abs(x))))
        #     d['angle'] = ang
        # if event.type == pg.USEREVENT:
        #     self.player.r_leg = not self.player.r_leg
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
        
        d['coords'] = pg.mouse.get_pos()
        # w,h = self.frame.get_size()
        # x,y = remap(x, (0, cfg.screen_h), (0,w)), remap(y, (0, cfg.screen_v), (0,h))
        # x, y =x+camera.x - self.player.rect.centerx, self.player.rect.centery - y - camera.y

        # d['look_r'] = x>=0
        # d['angle'] = angle((abs(x),-y))
        return d

    def procces_camera_shake(self):
        x, y = 0, 0
        if self.shake > 0:
            self.shake -= 1
            x = rd(-self.shake, self.shake)
            y = rd(-self.shake, self.shake)
        return x, y
        # x, y = 0, 0
        # if self.shake > 0.2:
        #     self.shake = self.shake*0.9       
        #     return self.shake,self.shake
        # return x, y
    
    @threaded()
    def get_frames(self):
        while 1:
            try:
                data = b''
                while 1:
                    d,add = self.sock.recvfrom(1024)
                    if add == self.addr:
                        if d == b'stop': break
                        else: data += d
                img = pg.image.fromstring(zlib.decompress(data),(854,480),'RGB')
                avg_color= pg.transform.average_color(img)
                if sum(avg_color)>700:continue
                self.screen.blit(img,(0,0))
            except socket.timeout: print('Frame recive timeout'); exit()
            except zlib.error: print('Bad frame')
            except Exception as e: print(e), exit()

    def draw(self):
        if self.online is not Status.Listen:
            if self.playing:
                self.world.draw(self.frame, pg.Rect(self.camera.x-40, self.camera.y-40,self.frame.get_width()+40,self.frame.get_width()+40),self.debug)
                # self.player.draw(self.frame, self.camera)

                # for p in self.players:
                #     p.draw(self.frame, self.camera)
                
                # POST PROCESS
                if not cfg.potato:
                    if self.world_tick!=1.0 or self.world.neo_mode:
                        self.screen.blit(self.tint_slow, (0, 0))
                    else:
                        self.screen.blit(self.tint, (0, 0))
                if self.w< sf.get_width():
                    sf.fill('black')
                    x,y = self.player.rect.centerx-self.camera.x, self.player.rect.centery-self.camera.y
                    x,y = remap(x, (0,854*self._curzoom),(0,cfg.screen_h)),remap(y, (0,480*self._curzoom),(0,cfg.screen_v))
                    pg.draw.circle(sf,'white', (x,y), round(self.w))
                    if self.player.dead:
                        text = font.render('Respawning...', False, (255,0,0))
                        text.set_alpha(remap(3000-self.player.die_kd, (1500,3000),(0,255)))
                        sf.blit(text, (300,100))
                    if self.w<cfg.screen_h-100:self.screen.blit(sf,(0,0))
                if self.debug:
                    debug(f'FPS: {int(self.clock.get_fps())} {"You have low FPS, game may work incorrect!" if self.fps_alert else ""}; Stream FPS:{int(self.stream_fps)}',self.frame)
                    debug(f'Actors: {len(self.world.actors)}', self.frame, y=15)
                    # debug(f'up:{self.player.on_ground} r:{self.player.right} l:{self.player.left}', self.frame, y=30)
                    debug(f'pos: {self.player.rect.center} ang: {self.player.angle} hp: {self.player.hp} slow_mo: {self.player.aim_time}', self.frame,y = 30,)
                    debug(f'{self.frame.get_size()} {self.camera.size}', self.frame,y = 45,)
                    debug(f'tick: {self.world_tick}',self.frame,y=60)
                    if self.online is Status.Host:
                        debug(f'players: {", ".join([f"{a}: {v[0]}" for a,v in self.addrs])}',self.frame,y=75)
            else:
                self.frame.fill('black')
            if self.world.neo_mode:
                neg = pg.Surface(self.frame.get_size())
                neg.fill((255, 255, 255))
                neg.blit(self.frame, (0, 0), special_flags=pg.BLEND_SUB)
                self.frame = neg
            if self.pause: self.screen.blit(self.tint2, (0, 0))
        self.ui.render(self.screen)

    def event_loop(self):
        global writing
        writing = pg.key.get_pressed()[pg.K_m]
        events = pg.event.get()
        for event in events:
            if pg.mouse.get_focused() :self.ui.update(event, self.delta)
            if hasattr(event, 'pos'):
                x,y = self.frame.get_size()
                setattr(event, 'pos', (remap(event.pos[0], (0, cfg.screen_h), (0,x)), remap(event.pos[1], (0, cfg.screen_v), (0,y))))

            if event.type == pg.QUIT: exit()
            if self.playing and event.type in [pg.KEYUP, pg.KEYDOWN, pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN,pg.MOUSEBUTTONUP, pg.MOUSEWHEEL, pg.USEREVENT]:
                self.player.process_move(self.update_control(event, self.camera))

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.pause_menu()
            if event.type == AUTOSAVE_EVENT:
                write_stats(self.stats)
                # write_stat('time', self.millis)
        return events


    def loop(self):
        events = self.event_loop()
        self.stats['time']+=self.delta/1000
        if self.playing and not self.pause:
            
            if self.player._delete: self.start_game(self.level)
            if self.v>self.w: self.w*=1.08
            else: self.w/=1.08
            self.world_tick = 0.3 if self.player.aiming else 1.0
            self.stats['time on ground' if self.player.on_ground else 'time in air']+=self.delta/1000
            self.player.update_control(self.delta*self.world_tick,self.world.get_blocks(self.player.pre_rect), self.world, self.world_tick)
            for i in self.addrs.values():
                i[1].update_control(self.delta*self.world_tick,self.world.get_blocks(self.player.pre_rect), self.world, self.world_tick)
            self.world.update_actors(self.delta*self.world_tick, self.player)


            self.camera_update()
            self.process_zoom()
            if self.clock.get_fps()<=35: self.fps_alert=True
        # pg.transform.scale(self.frame, self.res, self.screen)

        # ONLINE PROTOTYPE ----------------------
        if self.online!=Status.Listen:
            self.screen.blit(pg.transform.scale(self.frame, self.res), self.procces_camera_shake())
            self.draw()
        else:
            d= {}
            for e in events:
                if e.type in [pg.KEYUP, pg.KEYDOWN, pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN,pg.MOUSEBUTTONUP, pg.MOUSEWHEEL, pg.USEREVENT]:
                    d = {**d, **self.update_control(e, self.camera)}
            data = pickle.dumps(d)
            self.sock.sendto(data,self.addr)
        
        if self.online == Status.Host:
            for k in self.addrs.keys():
                self.addrs[k][0]-=self.delta
                if self.addrs[k][0]<=0: 
                    v = self.addrs.pop(k)
                    self.world.actors.remove(v[1])

        # ---------------------------------------

        
        pg.display.update()


    def run(self):
        print(repr(get_stat()))
        # self.resize()
        self.screen_stream()
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
