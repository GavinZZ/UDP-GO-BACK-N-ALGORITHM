import sys
import packet
import time
import math
import threading
from socket import *


def check_input():
    if len(sys.argv) != 5:
        print('Wrong Number of Arguments Given')
        exit()


def read_input(fileName):
    maxDataSize = 2
    file = open(fileName, "rb")
    contents = file.read()
    numPackets = math.ceil(len(contents)/maxDataSize)
    index = 0
    packets = []

    for i in range(numPackets):
        content = []
        for j in range(index, min(index+maxDataSize, len(contents))):
            content.append(contents[j])
        index += maxDataSize
        packet = bytes(content)
        packets.append(packet.decode("utf-8"))
    return packets


check_input()


# Define All the Variables
hostAddress = sys.argv[1]
emulatorPort = int(sys.argv[2])
senderPort = int(sys.argv[3])
fileName = sys.argv[4]
windowSize = 10
base = 0
nextseqnum = 0
startTime = 0
timeOut = 0.5
timerStarted = False
sndpkt = []
data = read_input(fileName)
udpSocket = socket(AF_INET, SOCK_DGRAM)
udpSocket.bind(('', senderPort))

# Creating Log files
seqLog = open("seqnum.log", "w+")
ackLog = open("ack.log", "w+")


def rcv_ack():
    global base, timerStarted, startTime, data
    while base < len(data):
        ack, clientAddress = udpSocket.recvfrom(2048)
        ackPacket = packet.packet.parse_udp_data(ack)
        if ackPacket is not None:
            ackNum = ackPacket.seq_num
            ackLog.write(str(ackNum)+"\n")
            # print("ACK"+str(ackNum % 32))
            if base % 32 == ackNum:
                base += 1
            elif ackNum > (base % 32) and (ackNum - base % 32) < windowSize:
                base += ackNum-base % 32 + 1
            elif ackNum < 10 and (ackNum + 32 - base % 32) < windowSize:
                base += ackNum + 32 - base % 32 + 1
            if base == nextseqnum:
                timerStarted = False
                # stop timer
            else:
                timerStarted = True
                startTime = time.time()


def send_pkt():
    global base, nextseqnum, timerStarted, data, timeOut, startTime
    while base < len(data):
        if nextseqnum < base+windowSize and nextseqnum < len(data):
            # print("SEQNUM"+str(nextseqnum % 32))
            seqLog.write(str(nextseqnum % 32)+"\n")
            sndpkt.append(packet.packet.create_packet(
                nextseqnum, data[nextseqnum % 32]))
            udpSocket.sendto(sndpkt[nextseqnum % 32].get_udp_data(),
                             (hostAddress, emulatorPort))
            if base == nextseqnum:
                startTime = time.time()
                timerStarted = True
            nextseqnum += 1
        else:
            # TIME OUT
            currTime = time.time()
            if (currTime - startTime > timeOut) and timerStarted:
                startTime = time.time()
                for i in range(base, nextseqnum):
                    seqLog.write(str(i % 32)+"\n")
                    # print("SEQNUM"+str(i % 32))
                    udpSocket.sendto(
                        sndpkt[i].get_udp_data(), (hostAddress, emulatorPort))

    # CREATE EOT TO SEND
    eotPacket = packet.packet.create_eot(nextseqnum % 32)
    udpSocket.sendto(eotPacket.get_udp_data(), (hostAddress, emulatorPort))

    while True:
        eot, clientAddress = udpSocket.recvfrom(2048)
        finalPacket = packet.packet.parse_udp_data(eot)
        if finalPacket.type == 2:
            ackLog.close()
            seqLog.close()
            return


def main():
    # MULTITHREADING
    thread = threading.Thread(target=rcv_ack)
    thread.start()

    send_pkt()


if __name__ == "__main__":
    main()
