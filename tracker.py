import struct
import bencode
import time
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
# -*- coding=utf-8 -*-
""" UDP """
trackerIP = '127.0.0.1'
trackerPort = 6789
peers = b''
peerAddrList = []


class service(DatagramProtocol):
    def datagramReceived(self, recvPacket, recvAddr):
        if not recvAddr in peerAddrList:
            peerJoin(recvAddr)
            peerAddrList.append(recvAddr)
        print("received %r from %s" % (recvPacket, recvAddr))
        print(recvPacket.decode())
        self.transport.write(recvPacket, recvAddr)  # send data to recvAddr
        print(peers)
        print(len(peers))
        port, = struct.unpack('!H', peers[4:6])
        print(port)
        time.sleep(1)


def peerJoin(addr):
    global peers
    ip, port = addr
    for num in ip.split('.'):
        peers += struct.pack('!B', int(num))  # unsigned char for 1 byte
    peers += struct.pack('!H', port)  # unsigned short for 2 bytes


# def peerRemove(addr):

if __name__ == '__main__':
    reactor.listenUDP(trackerPort, service(), trackerIP)
    reactor.run()
