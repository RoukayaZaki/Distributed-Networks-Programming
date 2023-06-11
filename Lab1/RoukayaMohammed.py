import socket
import argparse
import os


def receive_file(udp, file_path, file_size, addr):
    received = 0
    with open(file_path, 'wb') as f:
        while received < file_size:
            data, _ = udp.recvfrom(20480)
            f.write(data[4:])
            received += len(data)
            seqno = int(data[2])
            acknowledge(seqno, addr)
    print(f'Received {file_path}')


def handle_message(udp, message, addr):
    global file_path, file_name, file_size
    inspect = message.split('|')
    if inspect[0] == 's':
        file_name, file_size = inspect[2], int(inspect[3])
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.isfile(file_path):
            print(f'Overwriting existing file {file_name}...')
    elif inspect[0] == 'd':
        receive_file(udp, file_path, file_size, addr)
    else:
        print('Error: Unknown message type')
        return True
    acknowledge(int(inspect[1]), addr)
    return False


def acknowledge(seqno, addr):
    seqno = (seqno + 1) % 2
    ack = f'a|{seqno}'
    udp.sendto(ack.encode(), addr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    port = parser.parse_args()
    ip_addr = '0.0.0.0'
    # UDP socket for it
    udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp.bind((ip_addr, port.port))

    print(f'Listening at {ip_addr}:{port.port}')

    file_path = None
    file_name = None
    file_size = 0
    while True:
        data, addr = udp.recvfrom(20480)
        message = data.decode()
        if handle_message(udp, message, addr):
            break

    udp.close()
