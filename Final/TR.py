import sys
import select
import os
import struct
import socket
import argparse
import time

ETH_SIZE = 16
packet_id = 15987

def unpack_icmp_header(raw_data):
    ICMP = struct.unpack('!bbHHh', raw_data)
    return ICMP

def unpack_IP_header(raw_data):
    IP = struct.unpack('!BBHHHBBH4B4B', raw_data)
    return IP

def unpack_UDP_header(raw_data):
    UDP = struct.unpack('HHHH', raw_data)
    return UDP

def make_checksum(string):   
    sum = 0
    count = 0
    total_count = (len(string)/2)*2

    while (count < total_count):
        bi_val = string[count+1] *256 + string[count]
        sum = sum + bi_val
        sum = sum & 0xffffffff
        count = count +2

    if (total_count < len(string)):
        sum = sum + ord(string[len(string)-1])
        sum = sum & 0xffffffff

    sum = (sum>>16) + (sum&0xffff)
    sum = sum + (sum>>16)

    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def icmpheader(_seq, _data_size):
    data = ''
    ECHO = 8
    code = 0
    checksum = 0
    icmp_packet_id = packet_id
    seq = _seq

    for _ in range(0, _data_size):
        data = data + 'A'

    icmp_header = struct.pack("bbHHh", ECHO, code, checksum, socket.htons(icmp_packet_id), socket.htons(seq)) + data.encode('utf-8')
    checksum = make_checksum(icmp_header)
    icmp_header = struct.pack("bbHHh", ECHO, code, socket.htons(checksum), socket.htons(icmp_packet_id), socket.htons(seq)) + data.encode('utf-8')

    return icmp_header

def ipheader(_sor, _dst, _ttl, pro_option):
    version = 4
    header_length = 5
    tos = 0
    total_length = 0
    packet_id = 0
    flag = 0
    offset = 0
    ttl = _ttl

    if (pro_option == 'udp'):
        pro_option = 17
    elif (pro_option == 'icmp'):
        pro_option = 1
    checksum = 0

    sor_add = _sor.split('.')
    dst_add = _dst.split('.')
    sor_add = list(map(int, sor_add))
    dst_add = list(map(int, dst_add))
    sor = 0x00000000

    ip_header = struct.pack("!BBHHHBBHL4B", ((version & 0xff) <<4) + (header_length & 0xff), tos, total_length, packet_id, ((flag & 0xffff) << 13) + (offset & 0x1fff), ttl, pro_option, checksum, sor, dst_add[0], dst_add[1], dst_add[2], dst_add[3])
    
    return ip_header

def udpheader(_sor_port, _dst_port):
    data = ''
    sor_port = _sor_port
    dst_port = _dst_port
    header_len = 0
    checksum = 0

 

    udp_header = struct.pack("!HHHH", sor_port, dst_port, header_len, checksum)
    header_len = len(udp_header) + len(data)
    udp_header = struct.pack("!HHHH", sor_port, dst_port, header_len, checksum) + data.encode('utf-8')
	
    return udp_header

def icmp_ping(_sor, _dst, _time_out, _max_hop, _data_size):
    print(_dst + ' traceroute start max hops : ' + str(_max_hop))
    check = False
    sequence = 1
    time_check = ['*', '*', '*']
    ttl = 0
    basetime = 0
    thistime = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as send_sock:
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            for ttl in range(1, _max_hop + 1):
                respone = False
                packet = ipheader(_sor, _dst, ttl, 'icmp') + icmpheader(sequence, _data_size)
                print('step ' + str(ttl))
                for i in range(3):
                    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_sock:
                        recv_sock.settimeout(_time_out)
                        try:
                            send_sock.sendto(packet, (_dst, 0))
                            send_time = time.clock()

                            recv_packet, addr = recv_sock.recvfrom(65535)
                            recv_time = time.clock()

                            ip_length_cheack = struct.unpack('!B', recv_packet[0:1])
                            IPH_SIZE = (ip_length_cheack[0] & 0x0F) * 4
                            IPH_SIZE = 20
                            ip_hd = unpack_IP_header(recv_packet[0:IPH_SIZE])

                            thistime = round(((recv_time - send_time) * 10000), 2)
                            time_check[i] = str(round(((recv_time - send_time) * 10000 + basetime), 2)) + ' ms'

                            if ip_hd[6] != socket.IPPROTO_ICMP:
                                print('this is not icmp')
                                continue

                            icmp_hd = unpack_icmp_header(recv_packet[IPH_SIZE:IPH_SIZE+8])

                            if icmp_hd[0] == 0 and icmp_hd[1] == 0:
                                if icmp_hd[3] == packet_id and (str(ip_hd[8]) + '.' + str(ip_hd[9]) + '.' +  str(ip_hd[10]) + '.' +  str(ip_hd[11])) == _dst:
                                    print('complete')
                                    check = True
                                else:
                                    print('this is not mine')
                                    continue

                            elif icmp_hd[0] == 11 and icmp_hd[1] == 0:
                                if ((str(ip_hd[8]) + '.' + str(ip_hd[9]) + '.' +  str(ip_hd[10]) + '.' +  str(ip_hd[11])) != _dst or (str(ip_hd[12]) + '.' + str(ip_hd[13]) + '.' +  str(ip_hd[14]) + '.' +  str(ip_hd[15])) != _sor):
                                    print('ttl exceeded')
                                    continue

                            else:
                                continue

                        except socket.timeout:
                            print('time out')
                            for j in range(3):
                                time_check[j] = '*'
                            pass

                try:
                    if check:
                        print(socket.gethostbyaddr(addr[0])[0], end = ', ')
                        print(addr[0])
                        print(', '.join(time_check))
                        return
                    print(socket.gethostbyaddr(addr[0])[0], end = ', ')
                    print(addr[0])
                    
                except socket.herror:
                    print(addr[0])

                basetime = basetime + thistime

                print(', '.join(time_check))

                sequence += 1
                recv_sock.close()

    except socket.error as e:
        print(e)
        sys.exit(-1)

    send_sock.close()


def udp_ping(_sor, _dst, _time_out, _max_hop, _data_size, _sor_port):
    print(_dst + ' traceroute start max hops : ' + str(_max_hop))
    check = False
    port = 33434
    time_check = ['*', '*', '*']
    ttl = 0
    basetime = 0
    thistime = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as send_sock:
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            for ttl in range(1, _max_hop + 1):
                respone = False
                packet = ipheader(_sor, _dst, ttl, 'udp') + udpheader(_sor_port, port)
                print('step ' + str(ttl))
                for i in range(3):
                    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_sock:
                        recv_sock.settimeout(_time_out)
                        try:
                            send_sock.sendto(packet, (_dst, _sor_port))
                            send_time = time.clock()

                            recv_packet, addr = recv_sock.recvfrom(65535)
                            recv_time = time.clock()

                            ip_length_cheack = struct.unpack('!B', recv_packet[0:1])
                            IPH_SIZE = (ip_length_cheack[0] & 0x0F) * 4
                            ip_hd = unpack_IP_header(recv_packet[0:IPH_SIZE])

                            thistime = round(((recv_time - send_time) * 10000), 2)
                            time_check[i] = str(round(((recv_time - send_time) * 10000 + basetime), 2)) + ' ms'

                            if ip_hd[6] != socket.IPPROTO_ICMP:
                                print('this is not icmp')
                                continue

                            icmp_hd = unpack_icmp_header(recv_packet[IPH_SIZE:IPH_SIZE+8])

                            if icmp_hd[0] == 0 and icmp_hd[1] == 0:
                                if icmp_hd[3] == packet_id and (str(ip_hd[8]) + '.' + str(ip_hd[9]) + '.' +  str(ip_hd[10]) + '.' +  str(ip_hd[11])) == _dst:
                                    print('complete')
                                    check = True
                                else:
                                    print('this is not mine')
                                    continue

                            elif icmp_hd[0] == 11 and icmp_hd[1] == 0:
                                if ((str(ip_hd[8]) + '.' + str(ip_hd[9]) + '.' +  str(ip_hd[10]) + '.' +  str(ip_hd[11])) != _dst or (str(ip_hd[12]) + '.' + str(ip_hd[13]) + '.' +  str(ip_hd[14]) + '.' +  str(ip_hd[15])) != _sor):
                                    print('ttl exceeded')
                                    continue

                            else:
                                continue

                        except socket.timeout:
                            print('time out')
                            for j in range(3):
                                time_check[j] = '*'
                            pass

                try:
                    if check:
                        print(socket.gethostbyaddr(addr[0])[0], end = ', ')
                        print(addr[0])
                        print(', '.join(time_check))
                        return
                    print(socket.gethostbyaddr(addr[0])[0], end = ', ')
                    print(addr[0]) 
                except socket.herror:
                    print(addr[0])

                basetime = basetime + thistime

                print(', '.join(time_check))

                port += 1
                recv_sock.close()

    except socket.error as e:
        print(e)
        sys.exit(-1)

    send_sock.close()

if __name__ == '__main__':
    udp_check = False

    parser = argparse.ArgumentParser(description = '-d domain, -U pro type udp, -I pro type ICMP, -t recv timeout, -c max hops, -p udp port number')
    parser.add_argument('-host', type = str, required = True, metavar = 'domain', help = 'domain')
    parser.add_argument('-size', type = int, help = 'Data Size', default = 0)
    
    parser.add_argument('-t', type = int, help = 'recv time out', default = 3)
    parser.add_argument('-c', type = int, help = 'max hops', default = 30)

    parser.add_argument('-U', type = str, default = 'udp', nargs = '?')
    parser.add_argument('-I', type = str, default = 'icmp', nargs = '?')
    parser.add_argument('-p', type = int, help = 'UDP port number', default = 53)
    args = parser.parse_args()

    udp_check = args.U
    icmp_check = args.I
    sor = socket.gethostbyname(socket.gethostname())
    dst = socket.gethostbyname(args.host)
    data_size = args.size
    time_out = args.t
    max_hop = args.c
    sor_port = args.p
    if udp_check == None:
        print('use udp')
        udp_ping(sor, dst, time_out, max_hop, data_size, sor_port)
    elif icmp_check == None:
        print('use icmp')
        icmp_ping(sor, dst, time_out, max_hop, data_size)