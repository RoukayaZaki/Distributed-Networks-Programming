import socket
import io
from threading import Thread
from queue import Queue
import os
from PIL import Image
import random
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1234
SERVER_ADDR = (SERVER_HOST, SERVER_PORT) 
SERVER_BUFSIZE = 1024
global QUEUE
QUEUE = Queue()
        

def generate_image(width, height):
    pixels = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(width * height)]
    img = Image.new('RGB', (width, height))
    img.putdata(pixels)
    return img

def worker():
    global QUEUE
    while True:
        conn = QUEUE.get()
        pixels = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(10 * 10)]
        image = Image.new('RGB', (10, 10))
        image.putdata(pixels)
        output = io.BytesIO()
        image.save(output, format='PNG')
        data = output.getvalue()
        conn.sendall(data)
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(SERVER_ADDR)
        s.listen()
        THREADS = [Thread(target=worker) for i in range(10)]
        [t.start() for t in THREADS]
        try: 
            while True:
                conn, address = s.accept()
                global QUEUE
                QUEUE.put(conn)

                
        except KeyboardInterrupt:
            print('\nServer is shutting down')
            print('Done')
            os._exit(0)
        

if __name__ == "__main__":
    main()