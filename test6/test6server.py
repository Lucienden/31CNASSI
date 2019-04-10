import socket
import threading
import argparse
import time

def Send(Co):
    while True:
        Smsg = input()
        Co.send(Smsg.encode('utf-8'))
        print('\n')


def Recv(Co, Ad):
    while True:
        Rmsg = Co.recv(1024)
        print("%s : " %Ad[0], Rmsg.decode('utf-8'))
        print('\n')


def Cstart(conn, addr):
        print("connect with {} : {} ".format(addr[0], addr[1]))

        Se = threading.Thread(target = Send, args = (conn,))
        Re = threading.Thread(target = Recv, args = (conn, addr,))
        Se.start()
        Re.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thread server -p port")
    parser.add_argument('-p', help = "port_number", required = True)

    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(args.p)))
    server.listen(1)

    conn, addr = server.accept()#연결
    
    Cstart(conn, addr)

    while True:
        time.sleep(2)
        pass
    
    server.close()