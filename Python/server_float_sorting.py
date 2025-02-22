import socket
import struct
import threading
import sys

clients_data = []
clients_lock = threading.Lock()

def merge_sort(array):
    if len(array) > 1:
        mid = len(array) // 2
        L = array[:mid]
        R = array[mid:]

        merge_sort(L)
        merge_sort(R)

        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                array[k] = L[i]
                i += 1
            else:
                array[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            array[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            array[k] = R[j]
            j += 1
            k += 1
    return array

def worker(cs):
    global clients_data, clients_lock

    while True:
        N = struct.unpack('!I', cs.recv(4))[0]
        if N == 0:
            break

        client_data = []
        for _ in range(N):
            value = struct.unpack('!f', cs.recv(4))[0]
            client_data.append(value)

        with clients_lock:
            clients_data.extend(client_data)
            sorted_data = merge_sort(clients_data[:])

        cs.sendall(struct.pack('!I', len(sorted_data)))
        for value in sorted_data:
            cs.sendall(struct.pack('!f', value))
    cs.close()

if __name__ == '__main__':
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('172.30.247.36', 1234))
        server_socket.listen(5)
    except socket.error as msg:
        print("Error:", msg.strerror)
        exit(-1)

    print("Serverul rulează și așteaptă conexiuni...")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=worker, args=(client_socket,), daemon=True).start()
