import time
import socket, pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
message = pickle.dumps({'msg':'lol'})
addr = ("192.168.1.117", 5001)

def connect():
    try:
        client_socket.sendto(message, addr)
        data, server = client_socket.recvfrom(1024)
        d = data.decode()
        if d.startswith('ok'):
            print('Re: you can connect to server at port', d[2:])
        elif d.startswith('no'):
            print('Re: all servers are full RN')
        elif d.startswith('ta'):
            print('they lauching server for me) i just need to reconnect')
            time.sleep(0.5)
            connect()
            return
        print(data, server)
    except socket.timeout:
        print('Can t connect to servers :(')

print('waiting for answer')
connect()
