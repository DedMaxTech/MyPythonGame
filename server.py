import pygame as pg
import os, traceback, socket, pickle, logging, threading, time
from typing import List

import cfg, player, level

from editor import Editor

servers = []


class User:
    def __init__(self, addr, player=None, **data):
        self.addr = addr
        self.player = player
        # print().get('smth'))

    def __str__(self):
        return f'User at {self.addr}'


class Server:
    def __init__(self, port, max_players=4):
        self.users: List[User] = []
        self.port = port
        self.max_players = max_players
        self.running = True
        pg.init()

        self.t = threading.Timer(10, self.stop)
        self.pr = threading.Thread(target=self.awaiting_data, daemon=True)
        self.clock = pg.time.Clock()
        self.level = level.Level()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((socket.gethostbyname(socket.gethostname()), port))

        self.name = f'[SERVER at {port}]:'
        self.levelname = 'levels/level.txt'
        print(f'{self.name} started...')
        self.level.open_level(self.levelname)

    def awaiting_data(self):
        msg, addr = self.sock.recvfrom(1024)
        data = pickle.loads(msg)
        if addr not in [u.addr for u in self.users]:
            if len(self.users) < self.max_players:
                n = [i for i in range(self.max_players) if i not in [u.player.n for u in self.users]][0]
                p = player.Player(50, 50, n)
                self.users.append(User(addr, p, **data))
                self.sock.sendto(pickle.dumps({'msg': 'ok', 'n': n, 'level': open(self.levelname, 'r').readlines()}),
                                 addr)
        else:
            [u.player.process_move(data) for u in self.users if u.addr == addr]

    def send_data(self):
        for u in self.users:
            u.player.update(self.level.get_blocks(), self.level)
        ps = []
        for i in [u.player for u in self.users]:
            ps.append({'pos': i.rect.topleft, 'gun': i.gun, 'n': i.n, 'xspeed': i.xspeed, 'on_ground':i.on_ground, 'r_leg':i.r_leg, 'look_r':i.look_r})
        for u in self.users:
            self.sock.sendto(pickle.dumps({'ps': ps}), u.addr)

    def event_loop(self):
        for e in pg.event.get():
            if e.type == pg.USEREVENT and len(self.users) == 0: self.running = False

    def loop(self):
        if len(self.users) == 0 and not self.t.is_alive():
            self.t = threading.Timer(10, self.stop)
            self.t.start()
        if len(self.users) > 0: self.t.cancel()
        if not self.pr.is_alive():
            self.pr = threading.Thread(target=self.awaiting_data, daemon=True)
            self.pr.start()
        # print(f'{self.name} doing some shit....', self.users)
        self.send_data()

    def stop(self):
        self.running = False
        print(f'{self.name} commited suicide with no players :(')

    def run(self):
        while self.running:
            self.loop()
            self.clock.tick(60)
