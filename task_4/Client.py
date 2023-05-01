import struct
import threading
import socket
import time


def connect_to_fastest_server():
    servers_rtts = {}
    server_sockets = {}
    for server in SERVERS_PORTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', USERS_PORTS[user_index]))
            sock.connect(('127.0.0.1', server))

            start_time = time.time()
            sock.send(struct.pack('>bbhh', 5, 0, 0, 0))
            sock.recv(6)
            rtt = time.time() - start_time
            print(rtt)
            servers_rtts[server] = rtt
            server_sockets[server] = sock

        except Exception as e:
            print("Server [" + str(SERVERS_PORTS.index(server)) + "] didnt responde!")

    fastest_server = min(servers_rtts.items(), key=lambda x: x[1])[0]
    print("Server [" + str(SERVERS_PORTS.index(fastest_server)) + "] is the fastest!")

    # close rest
    for server in server_sockets:
        if server != fastest_server:
            conn = server_sockets[server]
            conn.send(struct.pack('>bbhh', 6, 0, 0, 0))
            print("Close connection with server[" + str(SERVERS_PORTS.index(server)) + "] ")
            conn.close()

    return server_sockets[fastest_server]


USERS_PORTS = [2222, 3333, 4444, 4545]
SERVERS_PORTS = [5555, 6666, 7777, 8888, 9999]

user_index = int(input("user index [0-2]: "))
sock = connect_to_fastest_server()

name = input('username: ')
msg_type = 2
sub_type = 1
sub_len = 0
name = name.encode()
msg_len = int(len(name))
data = struct.pack('>bbhh{}s'.format(msg_len), msg_type, sub_type, msg_len, sub_len, name)
print(data)
sock.send(data)


def output_recv():
    while True:
        try:
            header = sock.recv(6)
            msg_type, sub_type, msg_len, sub_len = struct.unpack('>bbhh', header)
        except struct.error as se:
            print(se)
            continue

        if msg_type == 2:
            data = sock.recv(msg_len)
            print("Server replay: " + str(data.decode()))

            message = input("put your message: ")
            reciver_name = input("receiver name: ")
            message = (name.decode() + '\0' + message + '\0' + reciver_name).encode()
            msg_len = len(message)
            msg_type = 3
            data = struct.pack('>bbhh{}s'.format(msg_len), msg_type, sub_type, msg_len, sub_len, message)
            sock.send(data)

        elif msg_type == 3:
            data = sock.recv(msg_len)
            print("new message! msg=" + str(data.decode('utf-8')))


x = threading.Thread(target=output_recv, args=()).start()
