#!/usr/bin/env python
import paho.mqtt.client as mqtt
import os
import socket
import struct
import binascii
import sys
import time

# Dash communication written by Bob Steinbeiser
# mqtt control by florolf / Niklas Fauth
rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                              socket.htons(0x0003))

mqttc = mqtt.Client()

mqttc.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASSWORD'])
mqttc.connect("mqtt.club.entropia.de", 1883, 60)
mqttc.loop_start()

whitelist = {"ac63bebc6aac" : "luefter"}

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

        if source_mac in whitelist:
            print "Dash button pressed!, IP = " + dest_ip + "MAC: " + source_mac + "Name: " + whitelist[source_mac]
            mqttc.publish("/public/dash/" + whitelist[source_mac])
            time.sleep(3)

    except ValueError:
        print "Error decoding ARP"

mqttc.disconnect()
