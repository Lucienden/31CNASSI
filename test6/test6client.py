import socket
import argparse
import threading
import time

def Send(So):
    while True:
        Smsg = input()
        So.send(Smsg.encode('utf-8'))
        print('\n')


def Recv(So, Ho):
    while True:
        Rmsg = So.recv(1024)
        print("%s : " %Ho, Rmsg.decode('utf-8'))
        print('\n')


def run(host, s):       
    Se = threading.Thread(target = Send, args = (s,))
    Re = threading.Thread(target = Recv, args = (s, host,))
    Se.start()
    Re.start() 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server =p port -i host")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-i', help="host_name", required=True)

    args = parser.parse_args()
    host, port = args.i, int(args.p)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print('connect success')

    run(host, s)
    while True:
        time.sleep(1)
        pass