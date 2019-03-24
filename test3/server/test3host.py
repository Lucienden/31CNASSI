import socket
import argparse
import os

def run_server(port, directory):
    host = ''

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)

        conn, addr = s.accept()
        filename = conn.recv(1024)
        FN = filename.decode('utf-8')
        os.chdir("%s" %directory)

        cou = 0
        for file_on_di in os.listdir("."):
                if file_on_di == FN:
                        cou = 1
                        data_transferred = 0
                        print("file name is : %s" %file_on_di)
                        print("fiel size : %d bytes" %os.path.getsize(file_on_di))
                        print("file send start---")
                        with open(file_on_di, 'rb') as F:
                                try:
                                        data = F.read(1024)
                                        while data:
                                                data_transferred += conn.send(data)
                                                data = F.read(1024)
                                except Exception as e:
                                        print(e)
                        print('send complete. size : %d' %data_transferred)
        if cou == 0:
                print("error")                        
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Echo server -p port -d directory')
    parser.add_argument('-p', help='port_number', required=True)
    parser.add_argument('-d', help='file_directory', required=True)

    args = parser.parse_args()
    run_server(port=int(args.p), directory=args.d)