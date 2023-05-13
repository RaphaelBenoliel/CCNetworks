import struct
import socket
import threading
server_Ip = ''
server_port = 0
my_name = ''
sock = None
try:
    server_Ip = '127.0.0.1'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_name = input('Enter your name: ')
    server_port = int(input("Enter server port: "))
    sock.connect((server_Ip, server_port))
except ConnectionRefusedError:
    print(server_Ip, server_port, ': not connected')

type = 2
subtype = 1
sublen = 0
dataName = my_name.encode()
length = len(dataName)

data = struct.pack('>bbhh{}s'.format(length), type, subtype, length, sublen, dataName)
sock.send(data)


def output_recvfrom(sock):
    global dataName
    while True:
        try:
            dataName = sock.recv(6)
        except Exception:
            print(': recv Error')
        if len(dataName) == 6:
            type, subtype, Len, sublen = struct.unpack('>bbhh', dataName)
            if type == 3:
                dataName = sock.recv(Len)
                dataName = struct.unpack('>{}s'.format(Len), dataName)[0].decode()
                print(dataName)


threading.Thread(target=output_recvfrom, args=(sock,)).start()

while True:
    receiver = input("Enter receiver name: ").strip().encode()
    data = input('Enter message for receiver: \n').strip().encode()
    data = receiver + b' ' + data
    type = 3
    subtype = 0
    sublen = len(receiver)
    dataName = data
    length = len(data)
    data = struct.pack('>bbhh{}s'.format(length), type, subtype, length, sublen, dataName)
    sock.send(data)
