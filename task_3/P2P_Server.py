import socket
import threading
import struct
import time


def encode_servers_dict():
    encoded_dict = ""
    for i in SERVERS:
        encoded_dict += str(i) + ':' + SERVERS[i] + '\0'
    return encoded_dict[:-1].encode()


def decode_servers_dict(encoded_dict):
    msg = ""
    for char in encoded_dict.decode("utf-8")[6:].replace('\0', ','):
        msg += char
    msg = msg.split(',')
    tuples = [(pair.split(':')[0], pair.split(':')[1]) for pair in msg]
    return dict(tuples)


def encode_users_list():
    encoded_list = ""
    for name in USERS:
        encoded_list += name + '\0'
    return encoded_list[:-1].encode()


def decode_users_list(encoded_list):
    msg = ""
    for char in encoded_list.decode("utf-8")[6:].replace('\0', ','):
        msg += char
    return msg.split(',')


def respond_to_client(conn_socket, client_address, client_name="client_name"):
    print('start listening from ', client_address)
    while True:
        try:
            message = conn_socket.recv(6)
            msg_type, sub_type, msg_len, sub_len = struct.unpack('>bbhh', message)
            print(struct.unpack('>bbhh', message))
        except struct.error as se:
            continue

        if msg_type == 0:
            if sub_type == 0:
                msg_type = 1
                sub_len = 0
                data = encode_servers_dict()
                msg_len = len(data)
                conn_socket.send(struct.pack(">bbhh{}s".format(msg_len), msg_type, sub_type, msg_len, sub_len, data))

            elif sub_type == 1:
                msg_type = 1
                sub_len = 0
                data = encode_users_list()
                msg_len = len(data)
                conn_socket.send(struct.pack(">bbhh{}s".format(msg_len), msg_type, sub_type, msg_len, sub_len, data))


        elif msg_type == 2:
            print("new user been Added")
            data = 'Hello User'.encode()
            msg_len = len(data)
            conn_socket.send(struct.pack(">bbhh{}s".format(msg_len), msg_type, sub_type, msg_len, sub_len, data))


def listen():
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        threading.Thread(target=respond_to_client, args=(conn, client_address)).start()

def connect_to_server(sock, port):
    if port == 0 or port in SERVERS_SOCKETS:
        return

    try:
        sock.send(struct.pack('>bbhh', 2, 0, 0, 0))
        SERVERS_SOCKETS[port] = sock
        print("Server [" + str(PORTS.index(port)) + "] been added")
    except Exception as e:
        print(e)

def send_to_server(other_index):
    try:
        sockConnect = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sockConnect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockConnect.bind(('127.0.0.1', PORTS[my_index]))
        sockConnect.connect(('127.0.0.1', PORTS[other_index]))
        if PORTS[other_index] not in SERVERS_SOCKETS:
            sockConnect.send(struct.pack('>bbhh', 2, 0, 0, 0))
            SERVERS_SOCKETS[PORTS[other_index]] = sockConnect
            print("Server [" + str(other_index) + "] been added")

        # servers
        data = struct.pack('>bbhh', 0, 0, 0, 0)
        sockConnect.send(data)
        servers = decode_servers_dict(sockConnect.recv(1024))
        print('server [' + str(other_index) + '] reply: ', servers)
        global SERVERS
        SERVERS[PORTS[other_index]] = '127.0.0.1'
        SERVERS.update(servers)
        for port in SERVERS:
            connect_to_server(sockConnect, port)

        # clients
        data = struct.pack('>bbhh', 0, 1, 0, 0)
        sockConnect.send(data)
        users = decode_users_list(sockConnect.recv(1024))
        print('server [' + str(other_index) + '] reply: ', users)
        global USERS
        USERS = list(set(USERS + users))


    except Exception as e:
        print('server ' + str(other_index) + ' did not respond')


PORTS = [1000, 1001, 1002, 1003, 1004]
SERVERS = {}
USERS = []
SERVERS_SOCKETS = {}

my_index = int(input("server index: "))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind(('0.0.0.0', PORTS[my_index]))
sock.listen()

threading.Thread(target=listen).start()

# connect to all other servers
for index in range(5):
    if index != my_index:
        threading.Thread(target=send_to_server, args=([index])).start()

