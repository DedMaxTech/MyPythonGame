import socket, threading, time
from server import Server

servers = []

def start_server(port, max_players=4):
    s = Server(port, max_players)
    servers.append(s)
    s.run()


class Router:
    def __init__(self, port: int, max_servers=1):
        self.max_servers = max_servers
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.procs = []

        addr = (socket.gethostbyname(socket.gethostname()), port)
        self.sock.bind(addr)
        print(f'Start routing at {addr}')

    def run_server(self):
        nmbrs = [int(str(s.port)[:-2]) for s in servers]
        for i in range(self.max_servers):
            if i not in nmbrs:
                if i == 0: i = 1
                t = threading.Thread(target=start_server, args=(self.port+i,), daemon=True)
                t.start()
                self.procs.append(t)
                print('started')
                break

    def check_servers(self):
        for s in servers:
            if not s.running:
                del servers[servers.index(s)]

    def loop(self):
        msg, addr = self.sock.recvfrom(1024)
        self.check_servers()
        print(f'someone at {addr} looking for server with msg: {msg}')
        if not servers:
            self.run_server()
            self.sock.sendto('ta'.encode(), addr)
            return
        available_ss = [s for s in servers if len(s.players) < s.max_players]
        if not available_ss and len(servers) < self.max_servers:
            self.run_server()
            self.sock.sendto('ta'.encode(), addr)
            return
        if not available_ss and len(servers) == self.max_servers:
            self.sock.sendto('no'.encode(), addr)
            return
        if available_ss:
            self.sock.sendto(f'ok{available_ss[0].port}'.encode(), addr)
            return

    def run(self):
        while True:
            self.loop()


if __name__ == '__main__':
    router = Router(5000, max_servers=10)
    router.run()
