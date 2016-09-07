import socket
import struct
import binascii
import sys
import time

# Dash communication written by Bob Steinbeiser
# Tornado control by Niklas Fauth

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                          socket.htons(0x0003))
MAC = 'ac63bebc6aac'
UDP_IP = "192.168.24.10"
UDP_PORT = 8888

while True:
    packet = rawSocket.recvfrom(2048)

    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack('!6s6s2s', ethernet_header)

    arp_header = packet[0][14:42]
    try:
        arp_detailed = struct.unpack('2s2s1s1s2s6s4s6s4s', arp_header)

        # skip non-ARP packets
        ethertype = ethernet_detailed[2]
        if ethertype != '\x08\x06':
            continue

        source_mac = binascii.hexlify(arp_detailed[5])
        dest_ip = socket.inet_ntoa(arp_detailed[8])
        #print "Dash button pressed!, IP = " + dest_ip + "MAC: " + source_mac
        if MAC == source_mac:
            print "Button pressed!"

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.sendto("what", (UDP_IP, UDP_PORT))
            data, server = sock.recvfrom(256)
            timeValue = int(data)
            print 'received: %d' % timeValue
            if timeValue == 0:
                sock.sendto("1023", (UDP_IP, UDP_PORT))
                data, server = sock.recvfrom(256)
                if "successfully" in data:
                    print "Luefter an!"
                if "locked" in data:
                    print "Lueter gelocked!"
                    sock.sendto("lock", (UDP_IP, UDP_PORT))
                    sock.sendto("1023", (UDP_IP, UDP_PORT))
                    print "Luefter an!"
            elif timeValue != 0:
                sock.sendto("0", (UDP_IP, UDP_PORT))
                data, server = sock.recvfrom(256)
                if "successfully" in data:
                    print "Luefter aus!"
                if "locked" in data:
                    print "Lueter gelocked!"
                    sock.sendto("lock", (UDP_IP, UDP_PORT))
                    sock.sendto("0", (UDP_IP, UDP_PORT))
                    print "Luefter aus!"
            time.sleep(3)
    except ValueError:
        print "Error decoding ARP"
