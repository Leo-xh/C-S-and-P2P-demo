import struct
import bencode
import threading
import time
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
# -*- coding=utf-8 -*-
""" UDP """
trackerIP = '127.0.0.1'
trackerPort = 6789
peerList = b''  # the peers list of compate format
peerTransID = []  # the list of peers' transaction id
timers = []


class service(DatagramProtocol):
    def datagramReceived(self, recvPacket, recvAddr):
        if not recvAddr in peerListAddrList:
            peerJoin(recvAddr)
        else:  # reset the timer for the peer
            index = peerListAddrList.index(recvAddr)
            timers[index].cancel()
            timers[index] = threading.timer(120, peerRemove, [recvAddr])
            timers[index].start()
        print("received %r from %s" % (recvPacket, recvAddr))
        print(recvPacket.decode())
        self.transport.write(recvPacket, recvAddr)  # send data to recvAddr
        print(peerList)
        print(len(peerList))
        port, = struct.unpack('!H', peerList[4:6])
        print(port)
        time.sleep(1)


def peerJoin(addr):
    ''' add the new peer into peerList and peerListAddrList '''
    global peerList, peerListAddrList, timers
    peerListAddrList.append(addr)
    ip, port = addr
    for num in ip.split('.'):
        peerList += struct.pack('!B', int(num))  # unsigned char for 1 byte
    peerList += struct.pack('!H', port)  # unsigned short for 2 bytes
    # set a timer for the new peer
    t = threading.timer(120, peerRemove, [addr])
    t.start()
    timers.append(t)


def peerRemove(addr):
    ''' rm the peer from peerList and peerListAddrList '''
    global peerList, peerListAddrList, timers
    index = peerListAddrList.index(addr)
    peerListAddrList.remove(addr)
    peerList = peerList[0:(index * 6)] + peerList[((index + 1) * 6):]
    del timers[index]


if __name__ == '__main__':
    reactor.listenUDP(trackerPort, service(), trackerIP)
    reactor.run()
