import socket
import argparse
import time
import struct
import select
import random
import math


port_set = 33434
max_hops = 30
timeout = 3

udp_code = socket.getprotobyname('udp')
icmp_code = socket.getprotobyname('icmp')
ICMP_ECHO = 8
udp_check = 0


def checksum(source):
    if(udp_check == 0):
        count = 0
        checkS = 0
        count_set = (len(source) / 2) * 2
    

        while (count < count_set):
            val = (source[count + 1]) * 256 + (source[count])
            checkS = checkS + val
            count = count + 2

        if (count_set < len(source)):
            checkS = checkS + (source[len(source) - 1])

        checkS = (checkS & 0xffff) + (checkS >> 16)
        checkS = checkS + (checkS >> 16)

        checkS_re = ~checkS
        checkS_re = checkS_re & 0xffff
        checkS_re = checkS_re >> 8 | (checkS_re << 8 & 0xff00)

        return checkS_re
    else:
        pass

def create_icmp_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO, 0, 0, id, 1)
    data = ''
    checksum_re = checksum(header + data.encode('utf-8'))

    header = struct.pack('bbHHh', ICMP_ECHO, 0, socket.htons(checksum_re), id, 1)
    return (header + data.encode('utf-8'))

def create_udp_packet(port):
    port = port >> 8 | (port << 8 & 0xff00)
    lenght = 9
    lenght = lenght >> 8 | (lenght << 8 & 0xff00)

    header = struct.pack('HHHH', port, port, lenght, 0)
    data = 'a'
    return (header + data.encode('utf-8'))



def icmp_receive_ping(socket_set, packet_id, time_sent, timeout):
    time_left = timeout

    while True:
        ready = select.select([socket_set], [], [], time_left)

        if (ready[0] == []):
            return 0

        time_received = time.time()
        rec_packet, addr = socket_set.recvfrom(1024)

        icmp_header = rec_packet[-8:]
        type, code, checksum, p_id, sequence = struct.unpack('bbHHh', icmp_header)
            

        if (p_id == packet_id):
            total_time_ms = (time_received - time_sent) * 1000
            total_time_ms = math.ceil(total_time_ms * 1000) / 1000
            return (addr[0], total_time_ms)
        time_left -= time_received - time_sent

        if (time_left <= 0):
            return 0

def udp_receive_ping(socket_set, time_sent ,timeout):#잘못된 코드
    time_left = timeout

    while True:
        ready = select.select([socket_set], [], [], time_left)

        if (ready[0] == []):
            return 0

        time_received = time.time()
        rec_packet, addr = socket_set.recevfrom(1024)
        print(addr + '\n')

        udp_header = rec_packet[-9:]
        sor, dst, lenght, check = struct.unpack('HHHH', udp_header)

        if (sor == dst):#조건을 바꿔야함
            total_time_ms = (time_received - time_sent) * 1000
            total_time_ms = math.ceil(total_time_ms * 1000) / 1000
            return (addr[0], total_time_ms)
        time_left -= time_received - time_sent

        if (time_left <= 0):
            return 0




def echo_start(host, ttl, sor):
    if (udp_check == 0):
        tracert = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_code)
        tracert.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        packet_id = int(random.random() * 65535)
        packet = create_icmp_packet(packet_id)

        while packet:
            sent = tracert.sendto(packet, (host, 1))
            packet = packet[sent:]

        ping = icmp_receive_ping(tracert, packet_id, time.time(), timeout)
        tracert.close()
        return ping
    else:
        tracert = socket.socket(socket.AF_INET, socket.SOCK_RAW, udp_code)
        tracert.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        packet_id = int(random.random() * 65535)
        packet = create_udp_packet(packet_id)

        while packet:
            sent = tracert.sendto(packet, (host, 1))
            packet = packet[sent:]

        ping = udp_receive_ping(tracert, time.time(), timeout)
        tracert.close()
        return ping

def echo(host, ttl, sor):
    try1 = echo_start(host, ttl, sor)
    try2 = echo_start(host, ttl, sor)
    try3 = echo_start(host, ttl, sor)
    
    if (try1 == 0):
        try1str = '*'
        try2str = '*'
        try3str = '*'

    else:
        try1str = try1[0] + ' - ' + str(try1[1]) + ' ms'
        try2str = str(try2[1]) + ' ms'
        try3str = str(try3[1]) + ' ms'
    
    print_str = str(ttl) + '  ' + try1str + ', ' + try2str + ', ' + try3str

    if (try1 == 0):
        dst_reached = False
    else:
        dst_reached = (try1[0] == host)

    return (print_str, dst_reached)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Traceroute')
    parser.add_argument('-d', required = True, help = 'Destination')
    parser.add_argument('-U', type = str, required = False, help = 'Protocol Type')
    args = parser.parse_args()

    if(args.U == 'u'):
        udp_check = 1
    
    dst_addr = args.d
    sor = socket.gethostbyname(socket.gethostname())
    host = socket.gethostbyname(dst_addr)
    print('TraceRoute start ' + dst_addr + ' ' + host + ', ' + str(max_hops) + ' hops max.')

    for i in range(1, max_hops+1):
        (print_str_u, dst_reached_u) = echo(host, i, sor)
        print(print_str_u)
        if dst_reached_u:
            break