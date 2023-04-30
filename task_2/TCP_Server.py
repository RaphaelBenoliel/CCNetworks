
# TCP server - lab2
import threading
import socket
# Array of port numbers
ports = [7012, 7001, 7002, 7003, 7004]


# Function to handle a connection
def handle_connection(conn, addr):
    print("New connection from", addr)
    data = conn.recv(1024)
    if data.decode() == "Hello":
        conn.send("World".encode())
        print("Completed connection with", addr)
        conn.close()


# Function to handle a server
def handle_server(port):
    # Create a socket and start listening on the given port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # set SO_REUSEADDR option
    server_socket.bind(("localhost", port))
    server_socket.listen(5)

    print("Listening on port", port)

    # Create a new thread to wait for accept
    threading.Thread(target=accept_connections, args=(server_socket,)).start()

    # Connect to other servers
    for other_port in ports:
        if other_port == port:
            continue

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(("localhost", other_port))
            client_socket.send("Hello".encode())
            data = client_socket.recv(1024)
            if data.decode() == "World":
                print("Completed connection with port", other_port)
        except ConnectionRefusedError:
            pass


# Function to accept incoming connections
def accept_connections(server_socket):
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_connection, args=(conn, addr)).start()


# Ask the user for an index to choose a port
index = int(input("Enter an index (0-4): "))
index_port = ports[index]

# Start a server on the chosen port
handle_server(index_port)
