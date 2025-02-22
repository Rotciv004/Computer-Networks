import socket
import threading
import time
import curses
from datetime import datetime
from collections import deque
import sys

# Global variables
PEER_LIST = {}
MALFORMED_MESSAGES = deque(maxlen=10)
MALFORMED_COUNT = 0
LOCK = threading.Lock()

UDP_PORT = 7777

def send_broadcast_message(broadcast_address, message):
    """Sends a broadcast message."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode() + b'\0', (broadcast_address, UDP_PORT))

def handle_received_message(data, addr, server_socket):
    """Processes received messages and sends appropriate responses."""
    global MALFORMED_COUNT, PEER_LIST

    try:
        message = data.decode().strip('\0')
        current_time = datetime.now()

        if message == "TIMEQUERY":
            response = f"TIME {current_time.strftime('%H:%M:%S')}\0"
            server_socket.sendto(response.encode(), addr)

        elif message == "DATEQUERY":
            response = f"DATE {current_time.strftime('%d:%m:%Y')}\0"
            server_socket.sendto(response.encode(), addr)

        else:
            # Count malformed messages
            with LOCK:
                MALFORMED_COUNT += 1
                MALFORMED_MESSAGES.append((addr[0], message))

        # Update peer list
        with LOCK:
            if addr in PEER_LIST:
                PEER_LIST[addr] = {
                    "last_seen": time.time(),
                    "date": current_time.strftime('%d:%m:%Y'),
                    "time": current_time.strftime('%H:%M:%S')
                }
            else:
                PEER_LIST[addr] = {
                    "last_seen": time.time(),
                    "date": current_time.strftime('%d:%m:%Y'),
                    "time": current_time.strftime('%H:%M:%S')
                }

    except Exception:
        # Handle malformed messages
        with LOCK:
            MALFORMED_COUNT += 1
            MALFORMED_MESSAGES.append((addr[0], data))

def listen_for_broadcasts(screen, broadcast_address):
    """Listens for UDP broadcasts and updates the peer list."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(('', UDP_PORT))
        while True:
            try:
                data, addr = server_socket.recvfrom(1024)
                threading.Thread(target=handle_received_message, args=(data, addr, server_socket)).start()
            except Exception:
                continue

def send_time_queries(broadcast_address):
    """Periodically sends TIMEQUERY broadcasts."""
    while True:
        send_broadcast_message(broadcast_address, "TIMEQUERY")
        time.sleep(3)

def send_date_queries(broadcast_address):
    """Periodically sends DATEQUERY broadcasts."""
    while True:
        send_broadcast_message(broadcast_address, "DATEQUERY")
        time.sleep(10)

def update_peer_list():
    """Removes peers not responding to broadcasts for 3 consecutive attempts."""
    while True:
        with LOCK:
            current_time = time.time()
            for addr in list(PEER_LIST):
                if current_time - PEER_LIST[addr]["last_seen"] > 9:  # 3 consecutive broadcasts (3s interval)
                    del PEER_LIST[addr]
        time.sleep(1)

def display_status(screen):
    """Displays peer list, malformed messages, and malformed count."""
    global PEER_LIST, MALFORMED_COUNT, MALFORMED_MESSAGES

    while True:
        screen.clear()
        screen.addstr(0, 0, "=== Peer List ===")
        with LOCK:
            for idx, (addr, details) in enumerate(PEER_LIST.items(), start=1):
                screen.addstr(idx, 0, f"{addr[0]} - DATE: {details['date']} TIME: {details['time']}")

            screen.addstr(len(PEER_LIST) + 2, 0, f"Malformed Messages Count: {MALFORMED_COUNT}")
            screen.addstr(len(PEER_LIST) + 4, 0, "=== Malformed Messages ===")

            for idx, (ip, msg) in enumerate(MALFORMED_MESSAGES, start=len(PEER_LIST) + 5):
                screen.addstr(idx, 0, f"{ip}: {msg}")

        screen.refresh()
        time.sleep(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python app.py <BROADCAST_ADDRESS>")
        sys.exit(1)

    broadcast_address = sys.argv[1]

    # Start listening thread
    threading.Thread(target=listen_for_broadcasts, args=(None, broadcast_address), daemon=True).start()
    # Start TIMEQUERY sending thread
    threading.Thread(target=send_time_queries, args=(broadcast_address,), daemon=True).start()
    # Start DATEQUERY sending thread
    threading.Thread(target=send_date_queries, args=(broadcast_address,), daemon=True).start()
    # Start peer list maintenance thread
    threading.Thread(target=update_peer_list, daemon=True).start()

    # Start the curses display
    curses.wrapper(display_status)

if __name__ == "__main__":
    main()
