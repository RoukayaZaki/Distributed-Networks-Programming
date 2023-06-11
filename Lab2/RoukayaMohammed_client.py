import os
import socket
import time
from threading import Thread
from PIL import Image
import multiprocessing

SERVER_URL = '127.0.0.1:1234'
FILE_NAME = 'RoukayaMohammed.gif'
CLIENT_BUFFER = 1024
FRAME_COUNT = 5000
FRAMES_PER_THREAD = 500
def download_frames(idx):
    t0 = time.time()
    global COUNT
    if not os.path.exists('frames'):
        os.mkdir('frames')
    for i in range(FRAMES_PER_THREAD):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            ip, port = SERVER_URL.split(':')
            s.connect((ip, int(port)))
            image = b''
            while True:
                packet = s.recv(CLIENT_BUFFER)
                if not packet:
                    break
                image += packet
            with open(f'frames/{idx * FRAMES_PER_THREAD + i}.png', 'wb') as f:
                f.write(image)
    return time.time() - t0

def process_frames(frame_ids):
    frames = []
    for frame_id in frame_ids:
        frame = Image.open(f"frames/{frame_id}.png").convert("RGBA")
        frames.append(frame)
    return frames

def create_gif():
    t0 = time.time()
    chunk_size = max(FRAME_COUNT // multiprocessing.cpu_count(), 1)
    with multiprocessing.Pool() as pool:
        frame_chunks = [range(i, min(i + chunk_size, FRAME_COUNT)) for i in range(0, FRAME_COUNT, chunk_size)]
        frames = pool.map(process_frames, frame_chunks)
    frames = [frame for chunk in frames for frame in chunk]
    frames[0].save(FILE_NAME, format="GIF", append_images=frames[1:], save_all=True, duration=500, loop=0)
    return time.time() - t0


if __name__ == '__main__':
    t0 = time.time()
    COUNT = 0
    THREADS = [Thread(target=download_frames, kwargs={"idx": i}) for i in range(10)]
    [t.start() for t in THREADS]
    [t.join() for t in THREADS]
    print(f"Frames download time: {time.time() - t0}")
    
    print(f"GIF creation time: {create_gif()}")
