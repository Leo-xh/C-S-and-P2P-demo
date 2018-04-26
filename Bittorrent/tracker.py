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


class service(DatagramProtocol):
    def datagramReceived(self, recvPacket, recvAddr):
        if len(recvPacket) < 16:
            return

        action, transactionID = struct.unpack("!II", recvPacket[8:])

        if action == 0:  # connect response
            ''' response a packet with 4-bytes action, transactionID, and connectionID '''
            print("Recevie connect request form %s:%d..." % recvAddr)
            print("Send connect response to %s:%d..." % recvAddr)
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
            connectionID, = struct.unpack("!Q", recvPacket)

            if len(recvPacket) < 98 or connectionID not in peerTimer:
                return

            print("Recevie announce request form %s:%d..." % recvAddr)
            print(
                "Send announce response with peer list to %s:%d..." % recvAddr)
            peerTimer[connectionID].cancle()
            if connectionID not in peerConnectID:
                ip, port = recvAddr  # need the external ip
                for num in ip.split('.'):
                    peerList += struct.pack('!B', int(num))
                peerList += recvPacket[96:98]
                peerConnectID.append(connectionID)

            interval = 30
            packet = struct.pack("!III", action, transactionID, interval)
            packet += peerList
            self.transport.write(packet, recvAddr)  # send peerList to client

            peerTimer[connectionID] = threading(2 * internel, peerRemove,
                                                [connectionID])
            peerTimer[connectionID].start()


def peerRemove(connectionID):
    ''' rm the peer from peerList and peerListAddrList '''
    global peerList, peerTimer, peerConnectID
    index = peerConnectID.index(connectionID)
    peerConnectID.remove(connectionID)
    peerList = peerList[0:(index * 6)] + peerList[((index + 1) * 6):]
    del peerTimer[connectionID]


def connectRequestTimeOut(infoHash, connectionID):
    del peerTimer[connectionID]


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