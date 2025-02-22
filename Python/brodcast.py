# Write an UDP broadcast application that serves as client and server at the same time. The application is started with the network broadcast address (<NBCAST>) as argument in the command line.
#
# 1.       Upon launching the application listens on UDP port 7777.
#
# 2.    Every 3 seconds the application sends a UDP broadcast message to NBCAST port 7777 with the format: TIMEQUERY\0 (string)
#
# 3.    Whenever the application receives a TIMEQUERY demand it answers to the source IP:port with a string message: TIME HH:MM:SS\0 (current time) using unicast.
#
# 4.    Every 10 seconds the application sends a UDP broadcast message to NBCAST port 7777 with the format:  DATEQUERY\0 (string)
#
# 5.    Whenever the application receives a DATEQUERY demand it answers to the source IP:port with a string message: DATE DD:MM:YYYY\0 (current date) using unicast.
#
# 6.    The application will keep a list of peers (that answer to broadcast – IP:portno) and update the information anytime a unicast message is received upon a broadcast.
#
# 7.    When an entry in a list does not have any answer for 3 consecutive broadcasts it will be removed from the list.
#
# 8.    The list will be displayed (ip,date, time) on the screen upon each update (using a screen positioning api like conio or by erasing the screen before each update).
#
# 9.    Every malformed request/response received will be counted and displayed at the end of a screen update. You will have a list of malformed messages displayed with their source IP address. The list should be limited in size and implemented as a queue. Recent messages are added to the head and old messages are moving towards the tail.
#
#
#
# Note: Suggestion: Implement the application on Windows, or run it on your laptop in order to be able (all of you simultaneously) to listen on port 7777. Your application should strictly follow the protocol and be able to interact with all applications written by your colleagues.
#
# Note: On Windows in order to have timer like events (periodical events handled) use timeSetEvent or a similar function (the newer  CreateTimerQueueTimer) and set a different callback function for each type of event.
#
# Note: Sending broadcast UDP requires a setsockopt(sock,SOL_SOCKET,SO_BROADCAST,&broadcast,sizeof(broadcast) as in example.
#
# Receiving broadcast usually doesn’t require any additional effort compared to a normal UDP application. If not able to receive broadcast on windows try to setsockopt  on the receiving socket as well.
#
# Note (Malformed traffic): To generate malformed traffic one could use the nc (network cat) command on a linux like system as it follows:
#
# nc -4 –u <dstip> <dstport>
#
#  and type in anything until CTRD+D is pressed ! Anything typed in will be sent to the the remote IP and port using the specified protocol (u=udp)
#
# or
#
# <command> | nc -4 –u 172.30.5.16 7777

import socket
import threading
import time
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

brodcastAdress = "255.255.255.255"

port = 7777
s.bind(('0.0.0.0',port))

TimeQueryString = b"TIMEQUERY"
DateQueryString = b"DATEQUERY"



peersList = []

def sendingDateQuery():
    global s, port, DateQueryString, brodcastAdress
    msg = DateQueryString
    while True:
        b = s.sendto(msg,(brodcastAdress , port))

        if b != len(msg):
            print("nothing was send\n date query\n")

        print("message sent\n")
        time.sleep(3)



def sendingTimeQuery():
    global s, port, TimeQueryString, brodcastAdress
    msg = TimeQueryString
    while True:
        b = s.sendto(msg, (brodcastAdress, port))

        if b != len(msg):
            print("nothing was send\n time query\n")

        print("message sent\n")
        time.sleep(10)



def respondQuery():
    global s, port, TimeQueryString, DateQueryString, peersList
    msg, adress= s.recvfrom(1024)

    print(f"message received: {msg} from ip: {adress[0]} and port: {adress[1]}")

    if msg == TimeQueryString:
        myTime = time.strftime(b"TIME %H:%M:%S")

        print(f"responding with {myTime} to ip: {adress[0]} and port: {adress[1]}")

        myTime = myTime.encode()

        b = s.sendto(myTime, adress)

        if b != len(myTime):
            print("nothing was send\n time query\n")

    elif msg == DateQueryString:
        myDate = time.strftime(b"DATE %d:%m:%Y")

        print(f"responding with {myDate} to ip: {adress[0]} and port: {adress[1]}")

        myDate = myDate.encode()

        b = s.sendto(myDate, adress)

        if b != len(myDate):
            print("nothing was send\n date query\n")

    #else:

        #if msg:

        #if adress[0] not in peersList.keys():
            #peersList[adress[0]] = (msg.decode(),3)


if __name__ == "__main__":
    args = sys.argv

    if len(args) <= 1:
        print("specify the brodecast adress")
        sys.exit(-1)

    brodcastAdress = args[1]

    thr1 = threading.Thread(target = sendingTimeQuery)
    thr2 = threading.Thread(target = sendingDateQuery)

    threads = []

    threads.append(thr1)
    threads.append(thr2)

    thr1.start()
    thr2.start()

    respondQuery()

    for t in threads:
        t.join()

