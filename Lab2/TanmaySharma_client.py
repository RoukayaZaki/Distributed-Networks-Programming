import os
import socket
import time

from PIL import Image
from threading import Thread
import multiprocessing

SERVER_URL = '127.0.0.1:1234'
FILE_NAME = 'TanmaySharma.gif'
CLIENT_BUFFER = 1024
FRAME_COUNT = 5000

divFactor = 500

# threading
def download_by_thread(slot):
    for i in range(divFactor):
        frameno = slot*divFactor + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            ip, port = SERVER_URL.split(':')
            s.connect((ip, int(port)))
            image = b''
            while True:
                packet = s.recv(CLIENT_BUFFER)
                if not packet:
                    break
                image += packet
            with open(f'frames/{frameno}.png', 'wb') as f:
                f.write(image)


def download_frames():
    t0 = time.time()
    if not os.path.exists('frames'):
        os.mkdir('frames')
    threads = []
    for i in range(FRAME_COUNT//divFactor):
        t = Thread(target=download_by_thread, kwargs={"slot": i})
        threads.append(t)
        t.start()

    for i in range(len(threads)):
        threads[i].join()
    return time.time() - t0



def thread_create_gif(index):
    frames = []
    for frame_id in range(625):
        frames.append(Image.open(f"frames/{frame_id + index}.png").convert("RGBA"))
    return frames

def create_gif():
    t0 = time.time()
    indexes = []
    for i in range(8):
        indexes.append(i*625)

    pool = multiprocessing.Pool(processes=8)
    frames = []
    combined_frames = pool.map(thread_create_gif, indexes)
    for i in range(len(combined_frames)):
        frames = frames + combined_frames[i]
    pool.close()
    pool.join()
    frames[0].save(FILE_NAME, format="GIF",
                   append_images=frames[1:], save_all=True, duration=500, loop=0)
    return time.time() - t0


if __name__ == '__main__':
    print(f"Frames download time: {download_frames()}")
    print(f"GIF creation time: {create_gif()}")
