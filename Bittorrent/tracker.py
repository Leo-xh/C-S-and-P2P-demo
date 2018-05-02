import struct
import bencode
import threading
import time
import random

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
# -*- coding=utf-8 -*-
""" UDP """
trackerIP = '127.0.0.1'
trackerPort = 56789
peerList = b''  # the peers' list of compate format
peerTimer = {}  # the dict of peers' timer with their connection id as key
peerConnectID = []  # the list of peers' connection id
peerAddrAndConnID = {}  # the peer address and their only connectionID


class service(DatagramProtocol):
    def datagramReceived(self, recvPacket, recvAddr):
        global peerList, peerTimer, peerConnectID
        if len(recvPacket) < 16:
            return

        action, transactionID = struct.unpack("!II", recvPacket[8:16])

        if action == 0:  # connect response
            ''' response a packet with 4-bytes action, transactionID, and connectionID '''
            print("Recevie connect request form %s:%d..." % recvAddr)
            print("Send connect response to %s:%d...\n" % recvAddr)
            connectionID, = generateConnectionID()
            packet = struct.pack("!IIQ", action, transactionID, connectionID)
            self.transport.write(packet, recvAddr)  # send response to recvAddr
            # set a timer(120s) for the connet request
            peerTimer[connectionID] = threading.Timer(
                120, connectRequestTimeOut, [connectionID])
            peerTimer[connectionID].start()

        elif action == 1:  # announce response
            ''' response a packet with 4-bytes action, transactionID, interval '''
            ''' and a peer list which has 4-bytes ip and 2-bytes port for each peer '''
            connectionID, = struct.unpack("!Q", recvPacket[0:8])

            if len(recvPacket) < 98 or connectionID not in peerTimer:
                return

            print("Recevie announce request form %s:%d..." % recvAddr)
            print("Send announce response with peer list to %s:%d...\n" %
                  recvAddr)
            peerTimer[connectionID].cancel()
            if connectionID not in peerConnectID:
                peerIP = recvAddr[0]  # need the external ip
                peerPort = (struct.unpack('!H', recvPacket[96:98]))[0]
                peerAddr = peerIP + ":" + str(peerPort)

                if peerAddr not in peerAddrAndConnID:
                    for num in peerIP.split('.'):
                        peerList += struct.pack('!B', int(num))
                    peerList += recvPacket[96:98]
                    peerConnectID.append(connectionID)

                else:  # replace peer's connectionID
                    connectionID_bak = peerAddrAndConnID[peerAddr]
                    if connectionID_bak in peerTimer:
                        peerTimer[connectionID_bak].cancel()
                        del peerTimer[connectionID_bak]
                    index = peerConnectID.index(connectionID_bak)
                    peerConnectID[index] = connectionID

                peerAddrAndConnID[peerAddr] = connectionID

            interval = 30
#            interval = 10
            packet = struct.pack("!III", action, transactionID, interval)
            packet += peerList
            self.transport.write(packet, recvAddr)  # send peerList to client
            peerTimer[connectionID] = threading.Timer(2 * interval, peerRemove,
                                                      [connectionID])
            peerTimer[connectionID].start()


def peerRemove(connectionID):
    ''' rm the peer from peerList and peerListAddrList '''
    global peerList, peerTimer, peerConnectID
    if connectionID in peerConnectID:
        index = peerConnectID.index(connectionID)
        peerConnectID.remove(connectionID)
        peerList = peerList[0:(index * 6)] + peerList[((index + 1) * 6):]
        del peerTimer[connectionID]


def connectRequestTimeOut(connectionID):
    del peerTimer[connectionID]
    peerRemove(connectionID)


def generateConnectionID():  # generate a 64-bits connection id
    byteNum = struct.pack("!I", int(time.time()))
    binayNum = ""
    while len(binayNum) < 32:
        binayNum = binayNum + str(random.randint(0, 1))
    byteNum += struct.pack("!I", int(binayNum, 2))
    return struct.unpack("!Q", byteNum)


if __name__ == '__main__':
    reactor.listenUDP(trackerPort, service(), trackerIP)
    reactor.run()
