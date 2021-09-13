import pygame as pg
import os, traceback, socket, pickle, logging, threading, time
from typing import List

import cfg, player, level

from editor import Editor

servers = []


class User:
    def __init__(self, addr, init_data: str):
        self.addr = addr
        print(pickle.loads(init_data.encode()).get('smth'))


class Server:
    def __init__(self, port, max_players=4):
        self.players: List[User] = []
        self.port = port
        self.max_players = max_players
        self.running = True
        pg.init()
        self.t = threading.Timer(10, self.stop)

        self.name = f'[SERVER at {port}]:'
        print(f'{self.name} started...')

    def event_loop(self):
        for e in pg.event.get():
            if e.type == pg.USEREVENT and len(self.players) == 0: self.running = False

    def loop(self):
        if len(self.players) == 0 and not self.t.is_alive():
            self.t = threading.Timer(10, self.stop)
            self.t.start()
        if len(self.players) > 0:
            self.t.cancel()
        print(f'{self.name} doing some shit....', self.players)
        time.sleep(5)

    def stop(self):
        self.running = False
        print(f'{self.name} commited suicide with no players :(')

    def run(self):
        while self.running:
            self.loop()
