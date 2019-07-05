import sys
import packet
from socket import *


def main():
    if len(sys.argv) != 5:
        print('Wrong Number of Arguments Given')
        exit()

    # Set up all variables
    hostAddress = sys.argv[1]
    receiverPort = int(sys.argv[2])
    emulatorPort = int(sys.argv[3])
    fileName = sys.argv[4]
    expectedseqnum = 0
    sndpkt = None

    # Set up log
    arrivalLog = open("arrival.log", "w+")
    dataFile = open(fileName, "w+")

    # Create UDP SOCKET
    udpServerSocket = socket(AF_INET, SOCK_DGRAM)
    udpServerSocket.bind(('', emulatorPort))

    while True:
        message, clientAddress = udpServerSocket.recvfrom(2048)
        rvdpkt = packet.packet.parse_udp_data(message)

        if rvdpkt.type == 2:
            # THIS IS A EOT PACKET
            eotPacket = packet.packet.create_eot(rvdpkt.seq_num)
            udpServerSocket.sendto(
                eotPacket.get_udp_data(), (hostAddress, receiverPort))
            arrivalLog.close()
            dataFile.close()
            return

        if rvdpkt.type == 1:
            # THIS IS A DATA PACKET
            arrivalLog.write(str(rvdpkt.seq_num)+"\n")
            # print("ARRIVAL:"+str(rvdpkt.seq_num))
            if rvdpkt.seq_num == expectedseqnum:
                dataFile.write(rvdpkt.data+"\n")
                sndpkt = packet.packet.create_ack(rvdpkt.seq_num)
                udpServerSocket.sendto(
                    sndpkt.get_udp_data(), (hostAddress, receiverPort))
                expectedseqnum = (expectedseqnum+1) % 32
            else:
                # SEND LAST SENT PACKET
                if expectedseqnum > 0:
                    udpServerSocket.sendto(
                        sndpkt.get_udp_data(), (hostAddress, receiverPort))


if __name__ == "__main__":
    main()
