import struct
import threading
import socket


PORTS = [1010, 1111, 1212]
SERVERS = [1000, 1001, 1002, 1003, 1004]

user_index = int(input("user index: "))
server_index = int(input("server index: "))
name = input('username: ')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind(('127.0.0.1', PORTS[user_index]))
sock.connect(('127.0.0.1', SERVERS[server_index]))

msg_type = 2
sub_type = 1
sub_len = 0

name = name.encode()
msg_len = int(len(name))


data = struct.pack('>bbhh{}s'.format(msg_len), msg_type, sub_type, msg_len, sub_len, name)
sock.send(data)


def output_recv():
    while True:
        header = sock.recv(6)
        msg_type, sub_type, msg_len, sub_len = struct.unpack('>bbhh', header)

        data = sock.recv(msg_len)
        print("Server [" + str(server_index) + "] replay: " + str(data.decode()))


x = threading.Thread(target=output_recv, args=()).start()
