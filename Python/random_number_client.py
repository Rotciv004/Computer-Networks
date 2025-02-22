import socket
import struct
import random
import sys
import time

if __name__ == '__main__':
    try:
        s = socket.create_connection(('172.30.248.211', 1234))
    except socket.error as msg:
        print("Error: ", msg.strerror)
        sys.exit(-1)

    random.seed()
    data = s.recv(1024)
    print(data.decode('ascii'))

    my_num = random.uniform(1.0, 100.0)
    try:
        s.sendall(struct.pack('!d', my_num))
        print(f'Sent {my_num}')
        result = s.recv(1024)
        print(result.decode('ascii'))
    except socket.error as msg:
        print('Error: ', msg.strerror)
        s.close()
        sys.exit(-2)

    s.close()
