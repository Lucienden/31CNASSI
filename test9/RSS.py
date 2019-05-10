import os
import socket
import argparse
import struct

ETH_P_ALL = 0x0003
ETH_SIZE = 14
IP_type_cheack = 0
IPH_SIZE = 0

def make_ethernet_header(raw_data):
	global IP_type_cheack
	ether = struct.unpack('!6B6BH', raw_data)
	if (ether[12] == 2048):
		IP_type_cheack = 1
		return {'Dst' : '%02x:%02x:%02x:%02x:%02x:%02x' %ether[:6],
			    'Src' : '%02x:%02x:%02x:%02x:%02x:%02x' %ether[6:12],
			    'Ether_Type' : ether[12]}
	else:
		IP_type_cheack = 0
		return {'Dst' : '%02x:%02x:%02x:%02x:%02x:%02x' %ether[:6],
			    'Src' : '%02x:%02x:%02x:%02x:%02x:%02x' %ether[6:12],
			    'Ether_Type' : ether[12]}

def make_IP_header(raw_data):
	IP = struct.unpack('!BBHHHBBH4B4B', raw_data)
	return {'Version' : (IP[0] >> 4),
		    'Header_Length ' : (IP[0] & 0x0F),
		    'Tos' : IP[1],
		    'Total_Length' : IP[2],
	    	'Identification' : IP[3],
	    	'Flag' : (IP[4] >> 13),
	    	'Offset' : (IP[4] & 0x1FFF),
	    	'Ttl' : IP[5],
	        'Protocol' : IP[6],
	    	'Checksum' : IP[7],
	    	'Src' : '%d:%d:%d:%d' %IP[8:12],
	    	'Dst' : '%d:%d:%d:%d' %IP[12:16]}

def dumpcode(buf):
	print("%7s"% "offset ", end='')
	for i in range(0, 16):
		print("%02x " % i, end='')
		if not (i%16-7):
			print("- ", end='')
	print("")

	for i in range(0, len(buf)):
		if not i%16:
			print("0x%04x" % i, end= ' ')
		print("%02x" % buf[i], end= ' ')

		if not (i % 16 - 7):
			print("- ", end='')

		if not (i % 16 - 15):
			print(" ")
	print("")

def sniffing(nic):
	global IP_type_cheack
	if os.name == 'nt':
		address_familiy = socket.AF_INET
		protocol_type = socket.IPPROTO_IP
	else:
		address_familiy = socket.AF_PACKET
		protocol_type = socket.ntohs(ETH_P_ALL)
	while(1):
		with socket.socket(address_familiy, socket.SOCK_RAW, protocol_type) as sniffe_sock:
			sniffe_sock.bind((nic, 0))
			if os.name == 'nt':
				sniffe_sock.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
				sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
			data, _ = sniffe_sock.recvfrom(65535)

			ethernet_header = make_ethernet_header(data[:ETH_SIZE])
			print('\n')
			print('Ethernet Header')
			for item in ethernet_header.items():
				print('[{0}] : {1}'.format(item[0], item[1]))
			print('\n')
			if(IP_type_cheack == 1):
				print('IP header')
				ip_length_cheack = struct.unpack('!B', data[ETH_SIZE:15])
				IPH_SIZE = (ip_length_cheack[0] & 0x0F) * 4
				ip_header = make_IP_header(data[ETH_SIZE:IPH_SIZE+14])
				for item in ip_header.items():
					print('[{0}] : {1}'.format(item[0], item[1]))
				IP_type_cheack = 0
			print('\n')
			print('Raw data')

			dumpcode(data)
			if os.name == 'nt':
				sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This is a simpe packet sniffer')
	parser.add_argument('-i', type=str, required=True, metavar='NIC name', help='NIC name')
	args = parser.parse_args()

	sniffing(args.i)