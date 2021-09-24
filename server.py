import pygame as pg
import os, traceback, socket, pickle, logging, threading, time, sys
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
    def __init__(self, port=None, max_players=4):
        self.users: List[User] = []
        self.port = port if port else cfg.addr[1]+1
        self.max_players = max_players
        self.running = True
        pg.init()

        self.t = threading.Timer(20, self.stop)
        self.pr = threading.Thread(target=self.awaiting_conn)
        self.workers_pool = []
        self.clock = pg.time.Clock()
        self.level = level.Level()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('10.0.0.69', port))
        print((socket.gethostbyname(socket.gethostname()), port))

        self.name = f'[SERVER at {port}]:'
        self.levelname = 'levels/level.txt' 
        print(f'{self.name} started...')
        self.level.open_level(self.levelname)

    def awaiting_data(self, conn:socket.socket,addr):
        n = [i for i in range(self.max_players) if i not in [u.player.n for u in self.users]][0]
        p = player.Player(50, 50, n)
        u = User(addr, p)
        self.users.append(u)
        conn.sendall(pickle.dumps({'msg': 'ok', 'n': n, 'level': open(self.levelname, 'r').readlines()}))
        while True:
            try:
                data = pickle.loads(conn.recv(1024))
                u.player.s = data
                print(len(self.users),{'ps':[u.player.s for u in self.users]})
                conn.sendall(pickle.dumps({'ps':[u.player.s for u in self.users]}))
            except Exception as e:
                print(e)
                conn.close()
                del self.users[self.users.index(u)]
                break

    def awaiting_conn(self):
        self.sock.listen(self.max_players)
        while True:
            conn, addr = self.sock.accept()
            print('new player ', addr)
            p = threading.Thread(target=self.awaiting_data, daemon=True, args=(conn,addr))
            p.start()
            # self.workers_pool.append(p)

    def send_data(self):
        for u in self.users:
            u.player.update(self.level.get_blocks(), self.level)
        # ps = []
        # for i in [u.player for u in self.users]:
        #     ps.append({'pos': i.rect.topleft, 'gun': i.gun, 'n': i.n, 'xspeed': i.xspeed, 'on_ground':i.on_ground, 'r_leg':i.r_leg, 'look_r':i.look_r})
        ps = [u.player.s for u in self.users]
        for u in self.users:
            self.sock.sendto(pickle.dumps({'ps': ps}), u.addr)

    def event_loop(self):
        for e in pg.event.get():
            if e.type == pg.USEREVENT and len(self.users) == 0: self.running = False

    def loop(self):
        if len(self.users) == 0 and not self.t.is_alive():
            self.t = threading.Timer(20, self.stop)
            self.t.start()
        if len(self.users) > 0: self.t.cancel()
        # if not self.pr.is_alive():
        #     self.pr = threading.Thread(target=self.awaiting_data)
        #     self.pr.start()
        # print(f'{self.name} doing some shit....', self.users)
        # self.send_data()

    def stop(self):
        self.running = False
        print(f'{self.name} commited suicide with no players :(')

    def run(self):
        self.pr.start()
        while self.running:
            self.loop()
            self.clock.tick(60)
            # print(self.clock.get_fps(), self.users)


if __name__ == '__main__':
    port = sys.argv[1]
    server = Server(int(port), 15)
    server.run()
