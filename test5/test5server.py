import socket
import threading
import argparse

def socket_handler(conn, addr):
    print("connect with {} : {} ".format(addr[0], addr[1]))
    msg = conn.recv(1024)
    msg.decode('utf-8')
    msg = msg[::-1]

    conn.sendall(msg)
    conn.close()
    print("disconnect with {} : {}".format(addr[0], addr[1]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thread server -p port")
    parser.add_argument('-p', help = "port_number", required = True)

    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(args.p)))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        th = threading.Thread(target=socket_handler, args=(conn, addr))
        th.start()

    server.close()
