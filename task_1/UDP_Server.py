import socket
# UDP server - lab1

UDP_IP = '0.0.0.0'
UDP_PORT = 9999
clients = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.bind((UDP_IP, UDP_PORT))
while True:
    data, addr = sock.recvfrom(1024)
    c_name = data.decode().rsplit(" ")[0]
    msg = data.decode().split()
    if c_name not in clients.keys() and len(msg) == 1 and addr not in clients.values():
        print(f'Welcome new client {c_name}')
        clients[c_name] = addr
        print(clients)
    else:
        name = data.decode().rsplit(' ')[0]
        if name not in clients.keys():
            sock.sendto(f'Sorry, client "{name}" is no exist'.encode(), addr)
        else:
            sock.sendto(data, clients.get(name))
