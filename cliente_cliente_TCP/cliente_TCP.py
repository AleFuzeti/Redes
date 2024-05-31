import socket
import threading
import time

# Socket create
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Choosing User 
user = ''

def recive_msg(connection):
    global stop_connection

    while True:
        try:
            message = connection.recv(1024)

            if mode == 'server':
                print(message.decode('utf-8'))
            else:
                print(message.decode('utf-8'))
        except:
            stop_connection = True
            break

def send_msg(connection):
    global stop_connection

    while True:
        msg = input() 

        if msg == '' or msg == 'exit' or msg == '\n':
            stop_connection = True
            break

        message = '{}: {}'.format(user, msg)
        print(message)
        connection.send(message.encode('utf-8'))

if __name__ == "__main__":
    # Connection Data
    while True:
        try:
            host = input("Enter host: ")
            break
        except socket.gaierror:
            print("[ERROR] invalid host, try again...")

    port = int(input("Enter port: "))
    user = input("Choose your username: ")
    stop_connection = False

while True:
    mode = input("Enter mode (client or server): ")
    if mode == "client":
        # Connecting to another client
        socket.connect((host, port))
        print("[CONNECTING] client connection established with host " + host + " on port " + str(port))
        
        # Recive a message from another client
        recive = threading.Thread(target = recive_msg, args = (socket,))
        recive.start()

        # Send a message to another client
        send = threading.Thread(target = send_msg, args = (socket,))
        send.start()
        break

    elif mode == "server":
        socket.bind((host, port))
        socket.listen(1)
        print("[STARTED] server is up and running on host " + host + " on port " + str(port))
        conn, addr = socket.accept()
        print("[CONNECTED] connection accepted with client " + str(addr))
        # Recive a message client
        recive = threading.Thread(target = recive_msg, args = (conn,))
        recive.start()
        # Send a message to client
        send = threading.Thread(target = send_msg, args = (conn,))
        send.start()

        break

    else:
        print("[ERROR] invalid mode...")
        continue

while True:
        if stop_connection:
            print("[CLOSE] connection closed...")
            send.join(1)
            recive.join(1)
            socket.close()
            
        time.sleep(1)