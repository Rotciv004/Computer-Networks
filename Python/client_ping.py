import socket
import time
import random
import sys


def send_ping(server_host, server_port, num_pings=5):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        for i in range(num_pings):
            message = str(random.randint(1000, 9999)).encode()  # Random content for PING
            start_time = time.time()
            client_socket.sendto(message, (server_host, server_port))

            try:
                client_socket.settimeout(1.0)  # 1 second timeout
                data, _ = client_socket.recvfrom(1024)
                end_time = time.time()
                rtt = (end_time - start_time) * 1000  # Convert to milliseconds

                if data == message:
                    print(f"PING {i + 1}: RTT = {rtt:.2f} ms - Matched")
                else:
                    print(f"PING {i + 1}: RTT = {rtt:.2f} ms - Content Mismatch")

            except socket.timeout:
                print(f"PING {i + 1}: Request timed out")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <server_port>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    send_ping(server_host, server_port)
