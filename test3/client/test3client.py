import socket
import argparse

def run(host, port, name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(name.encode('utf-8'))

        data = s.recv(1024)
        if not data:
                print('서버에 존재하지 않음')
                return

        with open('download/' + name, 'wb') as Fi:
                try:
                        while data:
                                Fi.write(data)
                                data_transferred = 0
                                data_transferred += len(data)
                                data = s.recv(1024)
                except Exception as e:
                        print(e)
        print('send complete. data size : %d' %data_transferred)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port -i host -f name")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-i', help="host_name", required=True)
    parser.add_argument('-f', help="file_name", required=True)

    args = parser.parse_args()
    run(host=args.i, port=int(args.p), name=args.f)