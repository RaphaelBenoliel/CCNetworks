import socket
import struct
import threading

arr = [2000, 2001, 2002, 2003, 2004]
my_Index = int(input("Enter your port index: "))
my_Port = arr[my_Index]
my_Ip = '127.0.0.1'
servers = {}
clientskn = {}
clientsks = {}
servers_connects_info = {}
milon = {"Raphael": 111, }

print(str(milon))


def handle_requests_from_connected_server(i, con_socket):
    global servers
    global clientskn
    global servers_connects_info

    while True:
        print(str(arr[i]) + " is listening")
        data = con_socket.recv(6)
        type, subtype, Len, sublen = struct.unpack('>bbhh', data)
        data = con_socket.recv(Len)
        if type == 1:
            if Len > 2:
                d1 = struct.unpack(">" + str(Len) + 's', data)[0].decode()
                for server_name in messageHandle(d1, ['{', '}']):
                    if server_name not in servers_connects_info.keys():
                        servers[server_name] = connect_to_server(server_name)
                        servers_connects_info[server_name] = my_Ip
        if type == 6 and subtype == 0:
            con_socket.send(struct.pack('>bbhh' + str(len(str(my_Port).encode())) + 's', 6, 1, len(str(my_Port).encode()), 0,
                                        str(my_Port).encode()))
        if type == 3 and subtype == 1:
            info = struct.unpack('>' + str(Len) + 's', data)[0].decode()
            info2 = info.split()
            if info2[0] in clientskn.keys():
                p = str(len(data)) + "s"
                message = struct.pack('>bbhh' + p, 3, 0, len(data), sublen, data)
                clientskn[info2[0]].send(message)
            else:
                for server_conn in servers.values():
                    if server_conn != con_socket:
                        p = str(len(info.encode())) + "s"
                        message = struct.pack('>bbhh' + p, 3, type + 1, len(info.encode()), sublen, info.encode())
                        server_conn.send(message)


def respond_to_request(conn_socket, client_address):
    global servers
    global clientskn
    global clientsks

    print('start listening to', client_address)
    while True:
        dat = conn_socket.recv(6)
        if len(dat) == 6:
            type, subtype, Len, sublen = struct.unpack('>bbhh', dat)
            if type == 0:
                if subtype == 0:
                    p = str(len(str(servers_connects_info).encode())) + "s"
                    message = struct.pack('>bbhh' + p, 1, subtype, len(str(servers_connects_info).encode()), 0,
                                          str(servers_connects_info).encode())
                    conn_socket.send(message)
                else:
                    p = str(len(str(clientskn))).encode() + "s"
                    message = struct.pack('>bbhh' + p, 1, subtype, len(str(clientskn).encode()), 0,
                                          str(clientskn).encode())
                    conn_socket.send(message)

            elif type == 2:
                if subtype == 1:
                    dat = conn_socket.recv(Len)
                    clientskn[(struct.unpack('>' + str(Len) + 's', dat)[0]).decode()] = conn_socket
                    clientsks[conn_socket] = struct.unpack('>' + str(Len) + 's', dat)[0].decode()
            elif type == 3:
                dat = conn_socket.recv(Len)
                info = struct.unpack('>' + str(Len) + 's', dat)[0].decode()
                if subtype == 0:
                    info = info.split()
                    print(info)
                    sender = clientsks[conn_socket].encode()
                    newdat = info[0].encode() + b' ' + sender
                    for i in range(len(info)):
                        if i != 0:
                            newdat = newdat + b' ' + info[i].encode()

                    if info[0] in clientskn.keys():
                        p = str(len(newdat)) + "s"
                        message = struct.pack('>bbhh' + p, 3, 0, len(newdat), len(sender + b' ' + info[0].encode()),
                                              newdat)
                        clientskn[info[0]].send(message)

                    else:
                        for i in servers.values():
                            p = str(len(newdat)) + "s"
                            message = struct.pack('>bbhh' + p, 3, 2, len(newdat), len(sender + b' ' + info[0].encode()),
                                                  newdat)
                            i.send(message)
                else:
                    info2 = info.split()
                    if info2[0] in clientskn.keys():
                        p = str(len(dat)) + "s"
                        message = struct.pack('>bbhh' + p, 3, 0, len(dat), sublen, dat)
                        clientskn[info2[0]].send(message)
                    else:
                        for i in servers.values():
                            if i != conn_socket:
                                print("info encode =", len(info.encode()))
                                p = str(len(info.encode())) + "s"
                                message = struct.pack('>bbhh' + p, 3, type + 1, len(info.encode()), sublen,
                                                      info.encode())
                                i.send(message)

            elif type == 6:
                print(type, subtype, Len, sublen)
                dat = conn_socket.recv(Len)
                print(dat)
                dat = struct.unpack('>' + str(Len) + 's', dat)[0].decode()
                print(dat)
                if dat not in servers_connects_info.keys():
                    servers[int(dat)] = conn_socket
                    servers_connects_info[int(dat)] = my_Ip
    conn_socket.close()


def listen(sock):
    while True:
        conn, client_address = sock.accept()
        print('new connection from', client_address)
        threading.Thread(target=respond_to_request, args=(conn, client_address)).start()
        message = struct.pack('>bbhh', 6, 0, 0, 0)
        conn.send(message)


def protocol(msg_type, sub_type, msg_len):
    global servers
    global clientskn
    global clientsks
    global servers_connects_info

    if msg_type == 0:
        if sub_type == 0:
            msg_len = len(servers)
            message = struct.pack('>iiii', 1, sub_type, 0, 0)
        elif sub_type == 1:
            print()

        print()
    elif msg_type == 1:
        print()
    elif msg_type == 2:
        print()
    elif msg_type == 3:
        print()

    return struct.pack('>bbhhs', 2, 0, 0, 0, '')


def create_server():
    global servers, con
    global clientskn
    global clientsks
    global servers_connects_info
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((my_Ip, my_Port))
    server_socket.listen(1)

    print("listening on port: ", my_Port)
    threading.Thread(target=listen, args=(server_socket,)).start()

    for i in range(len(arr)):
        if i != my_Index:
            try:
                if arr[i] not in servers_connects_info.keys():
                    con = connect_to_server(arr[i])
                    servers[arr[i]] = con
                    servers_connects_info[arr[i]] = my_Ip

                message = struct.pack('>bbhh', 0, 0, 0, 0)
                servers[arr[i]].send(message)
                j = i
                threading.Thread(target=handle_requests_from_connected_server, args=(j, con)).start()

            except ConnectionRefusedError:
                print(arr[i], ': not connected')


def messageHandle(d1, d2):
    for i in d2:
        d1 = d1.replace(i, '')
    arr = d1.split(',')
    addresses = []
    # print("arr = ", arr)
    for i in arr:
        address = int(i.split(':')[0])
        addresses.append(address)
    # print(addresses)
    return addresses


def connect_to_server(port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.connect((my_Ip, port))
    except ConnectionRefusedError:
        print(port, ': not connected')
        raise

    return server_socket


create_server()
