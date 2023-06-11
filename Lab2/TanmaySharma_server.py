# TCP connections imports
import io
from socket import socket, AF_INET, SOCK_STREAM, timeout
import time
from threading import Thread
import numpy
from PIL import Image

IP_ADDR = '127.0.0.1'
PORT = 1234
BUF_SIZE = 1024

connection_number = 0


def send_data(conn):
    imarray = numpy.random.rand(10, 10, 3) * 255
    im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    output = io.BytesIO()
    # we read images using IO buffer form im array to bytes
    # im.save is saving to output in format PNG
    im.save(output, format='PNG')
    data = output.getvalue()
    conn.sendall(data)
    conn.close()


# 1. create a TCP socket
# 2. bind the socket to address and port
# 3. start listening to port
s = socket(AF_INET, SOCK_STREAM)
s.bind((IP_ADDR, PORT))
s.listen()
# s.settimeout(5)

try:
    while True:
        try:
            print(f"Waiting for a new connection {time.time()}")
            conn, addr = s.accept()
            print(f"Accepted conn req from {addr}")
        except timeout:
            print(f"No connection request {time.time()}")
            s.settimeout(0)
        except Exception as e:
            print(e)
            break
        else:
            # conn.settimeout(3)
            # after accepting the client connection
            # spawn a new thread to handle the connection
            t = Thread(target=send_data, kwargs={"conn": conn})
            t.start()
            connection_number = connection_number + 1
            print(f"{connection_number}")
except KeyboardInterrupt:
    print(f"User has quit {time.time()}")
print("server is shutting down.")
