import socket
import threading
import struct
import time


def encode_servers_dict():
    encoded_dict = ""
    for i in SERVERS_ADDRESSES:
        encoded_dict += str(i) + ':' + SERVERS_ADDRESSES[i] + '\0'
    return encoded_dict[:-1].encode()


def decode_servers_dict(encoded_dict):
    msg = ""
    for char in encoded_dict.decode("utf-8")[6:].replace('\0', ','):
        msg += char
    msg = msg.split(',')
    tuples = [(int(pair.split(':')[0]), pair.split(':')[1]) for pair in msg]
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


def broadcast(data):
    data = data.encode()
    msg_type = 4
    sub_type = 0
    sub_len = 0
    msg_len = len(data)

    for server in SERVERS_ADDRESSES:
        if server != 0:
            try:
                print("broadcast msg to Server [" + str(SERVERS_PORTS.index(server)) + "] ")
                conn_socket = SERVERS_SOCKETS[server]
                conn_socket.send(struct.pack(">bbhh{}s".format(msg_len), msg_type, sub_type, msg_len, sub_len, data))
            except Exception as e:
                print(e)


def send_msg_to_user(sender, rcv, msg):
    msg = "[{0}:\0{1}]".format(sender, msg).encode()
    msg_type = 3
    sub_type = 0
    msg_len = len(msg)
    sub_len = 0
    conn_socket = USERS_ADDRESSES[rcv]
    data = struct.pack('>bbhh{}s'.format(msg_len), msg_type, sub_type, msg_len, sub_len, msg)
    conn_socket.send(data)


def respond_to_client(conn_socket, client_address, client_name="client_name"):
    while True:
        try:
            header = conn_socket.recv(6)
            msg_type, sub_type, msg_len, sub_len = struct.unpack('>bbhh', header)
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
            if sub_type == 0:
                print("Server [" + str(SERVERS_PORTS.index(client_address[1])) + "] been added")
                SERVERS_ADDRESSES[client_address[1]] = '127.0.0.1'
                SERVERS_SOCKETS[client_address[1]] = conn_socket

            elif sub_type == 1:
                try:
                    data = conn_socket.recv(msg_len).decode()
                    USERS.append(data)
                    USERS_ADDRESSES[client_address[1]] = conn_socket
                    print("User " + data + " been added")
                    data = ("Hello " + data).encode()
                    msg_len = len(data)
                    conn_socket.send(struct.pack(">bbhh{}s".format(msg_len), msg_type, 0, msg_len, sub_len, data))
                except Exception as e:
                    print(e)



        elif msg_type == 3:
            data = conn_socket.recv(msg_len).decode()
            sender, msg, rcv = data.split('\0')

            if rcv in USERS:
                send_msg_to_user(sender, rcv, msg)
            else:
                broadcast(data)


        elif msg_type == 4:
            sender, msg, rcv = conn_socket.recv(msg_len).decode().split('\0')
            print("beed broadcasted = " + str(msg))
            if rcv in USERS:
                send_msg_to_user(sender, rcv, msg)

        elif msg_type == 5:
            conn_socket.send(header)
            print("rtt check")

        elif msg_type == 6:
            print("Closing connection with: " + str(client_address))
            conn_socket.close()
            return


def listen():
    while True:
        conn, client_address = sock.accept()
        threading.Thread(target=respond_to_client, args=(conn, client_address)).start()


def connect_to_server(sock, port):
    if port == 0 or port in SERVERS_SOCKETS:
        return

    try:
        sock.send(struct.pack('>bbhh', 2, 0, 0, 0))
        SERVERS_SOCKETS[port] = sock
        print("Server [" + str(SERVERS_PORTS.index(port)) + "] been added")
    except Exception as e:
        print(e)


def inital_connection_with_server(other_index):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', SERVERS_PORTS[my_index]))
        sock.connect(('127.0.0.1', SERVERS_PORTS[other_index]))

        if SERVERS_PORTS[other_index] not in SERVERS_SOCKETS:
            sock.send(struct.pack('>bbhh', 2, 0, 0, 0))
            SERVERS_SOCKETS[SERVERS_PORTS[other_index]] = sock
            print("Server [" + str(other_index) + "] been added")

        # servers
        data = struct.pack('>bbhh', 0, 0, 0, 0)
        sock.send(data)
        servers = decode_servers_dict(sock.recv(1024))
        print('server [' + str(other_index) + '] reply: ', servers)
        global SERVERS_ADDRESSES
        SERVERS_ADDRESSES[SERVERS_PORTS[other_index]] = '127.0.0.1'
        SERVERS_ADDRESSES.update(servers)

        for port in SERVERS_ADDRESSES:
            connect_to_server(sock, port)

        # clients
        data = struct.pack('>bbhh', 0, 1, 0, 0)
        sock.send(data)
        users = decode_users_list(sock.recv(1024))
        print('server [' + str(other_index) + '] reply: ', users)
        global USERS
        USERS = list(set(USERS + users))


    except Exception as e:
        print('server ' + str(other_index) + ' did not respond')


SERVERS_PORTS = [5555, 6666, 7777, 8888, 9999]
SERVERS_ADDRESSES = {}
SERVERS_SOCKETS = {}
USERS = []
USERS_ADDRESSES = {}

my_index = int(input("Enter server index [0-4]: "))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind(('0.0.0.0', SERVERS_PORTS[my_index]))
sock.listen()

threading.Thread(target=listen).start()

# connect to all other servers
for index in range(5):
    if index != my_index:
        threading.Thread(target=inital_connection_with_server, args=([index])).start()

time.sleep(4)
print("SERVERS = " + str(SERVERS_ADDRESSES))
print("USERS = " + str(USERS))


